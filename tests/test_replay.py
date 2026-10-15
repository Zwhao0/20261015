"""T01–T14: hand-authored semantic assertions plus reviewed exact JSON fixtures."""

import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest

from observatory.engine import Replay, age_ms, canonical, replay
from observatory.__main__ import run
from tests.builders import event, exited, identity, line, manifest, status, terminal


FIXTURES = Path(__file__).parent / "fixtures"


class ReplayCases(unittest.TestCase):
    def play(self, values):
        return replay([line(v) if isinstance(v, dict) else v for v in values])

    def golden(self, case):
        raw = (FIXTURES / (case + ".jsonl")).read_bytes()
        actual = replay(raw.splitlines(keepends=True))
        expected = json.loads((FIXTURES / (case + ".expected.json")).read_text())
        self.assertEqual(actual, expected, case)
        self.assertEqual(canonical(actual), canonical(replay(raw.splitlines(keepends=True))))
        return actual

    def test_T01_process_attempt_run_success_are_separate(self):
        r = self.golden("T01")
        self.assertEqual([p["lifecycle"] for p in r["processes"]], ["EXITED_OK"])
        self.assertEqual([a["lifecycle"] for a in r["attempts"]], ["ATTEMPT_EXITED_OK"])
        self.assertEqual(r["runs"][0]["lifecycle"], "UNKNOWN")
        r = self.play([manifest(), exited(), terminal()])
        self.assertEqual(r["runs"][0]["lifecycle"], "COMPLETED")
        self.assertEqual(r["runs"][0]["key"], ["SYN_JOB", "SYN_RUN"])
        r = self.play([manifest(), exited(), terminal(proof="FINAL_ATTEMPT", final="SYN_ATTEMPT_0", no_restart=True)])
        self.assertEqual(r["runs"][0]["lifecycle"], "COMPLETED")
        for no_restart in [False, None]:
            r = self.play([manifest(), exited(), terminal(proof="FINAL_ATTEMPT", final="SYN_ATTEMPT_0", no_restart=no_restart)])
            self.assertEqual(r["runs"][0]["lifecycle"], "UNKNOWN")

    def test_T02_one_nonzero_is_not_whole_run_failure(self):
        r = self.golden("T02")
        self.assertEqual([e["lifecycle"] for e in r["exits"]], ["EXITED_NONZERO"])
        self.assertEqual(r["attempts"][0]["lifecycle"], "UNKNOWN")
        self.assertEqual(r["runs"][0]["lifecycle"], "UNKNOWN")
        self.assertEqual(len(r["attempts"][0]["failure_facts"]), 1)
        self.assertEqual(r["exits"][0]["root_cause"], "UNKNOWN")

    def test_T03_signal_does_not_prove_intent_or_root_cause(self):
        r = self.golden("T03")
        self.assertEqual(r["exits"][0]["lifecycle"], "EXITED_SIGNAL")
        self.assertIsNone(r["exits"][0]["expected_stop"])
        self.assertEqual(r["exits"][0]["root_cause"], "UNKNOWN")

    def test_T04_unknown_shell_encoding_stays_unknown(self):
        r = self.golden("T04")
        self.assertEqual(r["exits"], [])
        self.assertEqual(r["processes"][0]["lifecycle"], "UNKNOWN")
        for rc, state in [(0, "EXITED_OK"), (7, "EXITED_NONZERO"), (-15, "EXITED_SIGNAL"), (137, "EXITED_NONZERO")]:
            p = dict(raw_status=rc, raw_status_format="subprocess_returncode",
                     status_kind="SIGNALED" if rc < 0 else "EXITED", exit_code=rc if rc >= 0 else None,
                     signal=-rc if rc < 0 else None)
            r = self.play([exited(seq=0, **p)])
            self.assertEqual(r["exits"][0]["lifecycle"], state)
        r = self.play([exited(seq=0, raw_status=15, exit_code=0)])
        self.assertEqual(r["counts"]["invalid"], 1)
        self.assertEqual(r["exits"], [])

    def test_T05_partial_identity_never_binds(self):
        r = self.golden("T05")
        self.assertEqual(r["processes"], [])
        self.assertEqual(r["exits"], [])
        for field in ["pid_namespace_id", "process_start_ticks", "job_id", "rank", "gpu_uuids"]:
            r = self.play([exited(seq=0, ident=identity(**{field: None}))])
            self.assertEqual(r["exits"], [], field)
        bad = exited(seq=0)
        del bad["identity"]["pid_namespace_id"]
        r = self.play([bad, event(seq=1)])
        self.assertEqual(r["counts"]["invalid"], 1)
        self.assertEqual(r["processes"][0]["lifecycle"], "UNKNOWN")

    def test_T06_pid_reuse_new_attempt_and_boot_are_isolated(self):
        r = self.golden("T06")
        self.assertEqual([p["lifecycle"] for p in r["processes"]], ["EXITED_OK", "UNKNOWN", "UNKNOWN"])
        self.assertEqual([a["lifecycle"] for a in r["attempts"]], ["UNKNOWN", "UNKNOWN"])
        self.assertEqual(len(r["runs"]), 1)
        r = self.play([exited(seq=0), event(seq=1, ident=identity(boot_id="SYN_BOOT_NEW"))])
        self.assertEqual(len(r["processes"]), 2)
        self.assertEqual(len(r["exits"]), 1)

    def test_T07_periodic_stale_event_idle_failure_recovery(self):
        r = self.golden("T07")
        self.assertEqual([s["status"] for s in r["sources"]], ["STALE", "IDLE", "UNKNOWN"])
        self.assertEqual(r["exits"], [])
        for ms, expected in [(15000, "OK"), (15001, "STALE")]:
            r = self.play([status(mode="PERIODIC", state="OK", age=ms)])
            self.assertEqual(r["sources"][0]["status"], expected)
        r = self.play([status(state="UNAVAILABLE", read="UNAVAILABLE"), status(seq=1, age=3_600_000)])
        self.assertEqual(r["sources"][0]["status"], "IDLE")
        self.assertEqual(r["sources"][0]["history"], ["UNAVAILABLE"])
        self.assertEqual(r["sources"][0]["coverage_status"], "UNKNOWN")
        self.assertEqual(r["exits"], [])

    def test_T08_duplicate_late_snapshot_conflict(self):
        r = self.golden("T08")
        self.assertEqual(r["counts"]["duplicates"], 1)
        self.assertEqual(len(r["exits"]), 1)
        self.assertEqual(r["processes"][0]["lifecycle"], "EXITED_OK")
        a, b = exited(seq=0), exited(seq=0, code=7)
        r = self.play([a, b])
        self.assertEqual([d["code"] for d in r["diagnostics"]], ["CONFLICT"])
        self.assertEqual(r["exits"], [])
        cross = exited(seq=0, source="SYN_SOURCE_B")
        r = self.play([a, cross])
        self.assertEqual(len(r["exits"]), 1)
        self.assertEqual(len(r["exits"][0]["evidence_refs"]), 2)
        cross["payload"].update(raw_status=7 * 256, exit_code=7)
        r = self.play([a, cross])
        self.assertEqual(r["exits"], [])
        self.assertEqual(r["processes"][0]["lifecycle"], "UNKNOWN")
        ordered = self.play([manifest(), event(seq=1), exited(seq=2)])
        reordered = self.play([exited(seq=2), manifest(), event(seq=1)])
        for field in ["sources", "processes", "attempts", "runs", "exits"]:
            self.assertEqual(ordered[field], reordered[field], field)

    def test_T09_time_domains_and_wall_clock_rollback(self):
        r = self.golden("T09")
        self.assertEqual([p["last_observed_age_ms"] for p in r["processes"]], [2.0, None])
        self.assertEqual(age_ms(10, "SYN_A", 9, "SYN_A"), None)
        self.assertEqual(age_ms(0, "SYN_A", 2_000_000, "SYN_A"), 2.0)
        self.assertEqual(age_ms(0, "SYN_A", 2_000_000, "SYN_B"), None)
        e = event()
        e["time"]["event_time_utc"] = "bad"
        r = self.play([e])
        self.assertEqual(r["counts"]["invalid"], 0)
        self.assertIsNone(r["events"][0]["record"]["time"]["event_time_utc"])
        self.assertIn("time.event_time_utc", r["events"][0]["record"]["unknown_reasons"])

    def test_T10_bad_frames_schema_gap_and_recovery(self):
        r = self.golden("T10")
        self.assertEqual([d["code"] for d in r["diagnostics"]], ["INVALID_RECORD", "INVALID_RECORD", "INCOMPLETE_FRAME"])
        self.assertEqual(r["sources"][0]["status"], "GAP")
        self.assertEqual(r["counts"]["accepted"], 2)
        r = self.play([status(state="GAP"), status(seq=1)])
        self.assertEqual(r["sources"][0]["status"], "IDLE")
        self.assertEqual(r["sources"][0]["history"], ["GAP"])
        r = self.play([status(), status(seq=10**18)])
        self.assertTrue(r["sources"][0]["sequence_gap"])
        r = self.play([status(seq=4), status(seq=3)])
        self.assertFalse(r["sources"][0]["sequence_gap"])
        r = self.play([status(), status(seq=0, source="SYN_SOURCE_B")])
        self.assertEqual(len(r["sources"]), 2)
        r = self.play([status(), b'\xff\n', event(seq=1)])
        self.assertEqual(r["counts"]["accepted"], 2)

    def test_T11_progress_missing_unchanged_and_metrics_error(self):
        r = self.golden("T11")
        records = [e["record"] for e in r["events"] if e["record"]["event_type"] == "SNAPSHOT"]
        self.assertIsNone(records[0]["payload"]["progress"])
        self.assertEqual([e["payload"]["progress"]["step"] for e in records[1:]], [0, 0])
        metric = records[-1]["payload"]["device_samples"][0]["metrics"]["utilization"]
        self.assertIsNone(metric["value"])
        self.assertEqual(metric["status"], "ERROR")
        self.assertEqual(r["processes"][0]["lifecycle"], "UNKNOWN")
        self.assertEqual(r["exits"], [])

    def test_T12_launcher_locality_and_expected_cancel(self):
        r = self.golden("T12")
        self.assertEqual(len(r["exits"]), 1)
        self.assertTrue(r["exits"][0]["expected_stop"])
        self.assertEqual(r["runs"][0]["lifecycle"], "UNKNOWN")
        self.assertEqual([p["lifecycle"] for p in r["processes"] if p["key"][3] == "worker"], ["UNKNOWN"])

    def test_T13_privacy_unknown_fields_limits_and_cli(self):
        r = self.golden("T13")
        self.assertEqual(r["events"], [])
        self.assertEqual(r["counts"]["invalid"], 4)
        self.assertEqual(r["processes"], [])
        for mutate in [lambda e: e.update(origin="REAL"),
                       lambda e: e["identity"].update(host_id="real-host"),
                       lambda e: e.update(evidence_ref="/private/path"),
                       lambda e: e["payload"].update(token="sk-secret")]:
            e = event()
            mutate(e)
            r = self.play([e])
            self.assertEqual(r["counts"]["invalid"], 1)
            self.assertNotIn("private/path", canonical(r))
            self.assertNotIn("sk-secret", canonical(r))
        engine = Replay(1)
        for _ in range(100):
            engine.feed(line(event()))
        self.assertEqual(len(engine.diagnostics), 1)
        self.assertEqual(engine.result()["diagnostics"][0]["code"], "QUEUE_LIMIT")
        out, err = io.StringIO(), io.StringIO()
        rc = run(io.BytesIO(b"x" * 20000 + b"\n" + line(event())), out, err)
        self.assertEqual(rc, 1)
        rows = [json.loads(x) for x in out.getvalue().splitlines()]
        self.assertEqual(rows[-1]["counts"]["accepted"], 1)
        self.assertEqual(rows[-2]["code"], "LINE_LIMIT")
        self.assertEqual(err.getvalue(), "")
        fixture = str(FIXTURES / "T01.jsonl")
        a = subprocess.run([sys.executable, "-m", "observatory", fixture], capture_output=True)
        b = subprocess.run([sys.executable, "-m", "observatory", fixture], capture_output=True)
        self.assertEqual((a.returncode, a.stderr), (0, b""))
        self.assertEqual(a.stdout, b.stdout)
        self.assertEqual(hashlib.sha256(a.stdout).digest(), hashlib.sha256(b.stdout).digest())
        bad = subprocess.run([sys.executable, "-m", "observatory", "-"], input=b"not-json\n", capture_output=True)
        self.assertEqual(bad.returncode, 1)
        self.assertEqual(json.loads(bad.stdout.splitlines()[-1])["counts"]["accepted"], 0)

    def test_T14_missing_members_restart_and_final_proofs(self):
        r = self.golden("T14")
        self.assertEqual(r["attempts"][0]["lifecycle"], "UNKNOWN")
        self.assertEqual(r["runs"][0]["lifecycle"], "UNKNOWN")
        r = self.play([manifest(ident=identity(world_size=2), members=[identity(world_size=2), identity(world_size=2, rank=1, pid=101)]),
                       exited(ident=identity(world_size=2)),
                       terminal(proof="FINAL_ATTEMPT", final="SYN_ATTEMPT_0", no_restart=True)])
        self.assertEqual(r["runs"][0]["lifecycle"], "UNKNOWN")
        r = self.play([manifest(ident=identity(world_size=2), members=[identity(world_size=2), identity(world_size=2, rank=1, pid=101)]),
                       exited(ident=identity(world_size=2)), terminal()])
        self.assertEqual(r["runs"][0]["lifecycle"], "COMPLETED")
        self.assertEqual(r["attempts"][0]["lifecycle"], "UNKNOWN")
        r = self.play([terminal(seq=0), terminal(seq=1, outcome="FAILED")])
        self.assertEqual(r["runs"][0]["lifecycle"], "UNKNOWN")
        for outcome in ["FAILED", "CANCELLED"]:
            r = self.play([terminal(seq=0, outcome=outcome)])
            self.assertEqual(r["runs"][0]["lifecycle"], outcome)


if __name__ == "__main__":
    unittest.main()
