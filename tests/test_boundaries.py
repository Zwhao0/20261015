"""Adversarial and semantic regressions independent of golden snapshots."""

import hashlib
from pathlib import Path
import io
import json
import unittest
from unittest.mock import patch

from observatory.engine import MAX_LINE_BYTES, Replay, canonical, replay
from observatory.__main__ import run
from tests.builders import event, exited, identity, line, manifest, status, terminal


def play(*records):
    return replay([line(r) if isinstance(r, dict) else r for r in records])


class Boundaries(unittest.TestCase):
    def test_fixture_input_and_expected_hashes_are_frozen(self):
        root = Path(__file__).parent / "fixtures"
        manifest = json.loads((root / "manifest.json").read_text())
        self.assertEqual(len(manifest), 28)
        for name, expected in manifest.items():
            self.assertEqual(hashlib.sha256((root / name).read_bytes()).hexdigest(), expected, name)

    def test_bounded_iterable_and_bad_frame_io(self):
        consumed = []
        def rows():
            while True:
                consumed.append(1)
                yield line(event())
        r = replay(rows(), max_records=2)
        self.assertEqual(len(consumed), 3)
        self.assertEqual(r["diagnostics"][0]["code"], "QUEUE_LIMIT")
        class InfiniteFrame:
            read_bytes = 0
            def readline(self, size):
                self.read_bytes += size
                return b"x" * size
        stream = InfiniteFrame()
        out, err = io.StringIO(), io.StringIO()
        self.assertEqual(run(stream, out, err), 1)
        self.assertLessEqual(stream.read_bytes, 1024 * 1024)
        rows = [json.loads(x) for x in out.getvalue().splitlines()]
        self.assertEqual([r["code"] for r in rows[:-1]], ["LINE_LIMIT", "FRAME_READ_LIMIT"])
        engine = Replay(3)
        for e in [manifest(), exited(), terminal(), event(seq=3)]:
            engine.feed(line(e))
        self.assertEqual(engine.result()["runs"][0]["lifecycle"], "UNKNOWN")
        for category in ["sources", "processes", "attempts", "runs"]:
            self.assertTrue(all(r["coverage_status"] == "UNKNOWN" for r in engine.result()[category]))
        r = play(status(), event(seq=1), b"x" * 16385 + b"\n")
        self.assertEqual(r["sources"][0]["coverage_status"], "UNKNOWN")
        self.assertEqual(r["processes"][0]["coverage_status"], "UNKNOWN")

    def test_manifest_mapping_and_terminal_evidence_are_not_interchangeable(self):
        r = play(manifest(), manifest(seq=1, members=[identity(gpu_uuids=["SYN_GPU_CHANGED"])]))
        self.assertEqual(r["attempts"][0]["identity_status"], "UNKNOWN")
        r = play(manifest(), exited())
        self.assertEqual(r["attempts"][0]["terminal_evidence_ref"], "SYN_EVIDENCE_SYN_SOURCE_A_1")
        self.assertEqual(r["attempts"][0]["terminal_evidence_refs"], ["SYN_EVIDENCE_SYN_SOURCE_A_1"])

    def test_source_freshness_uses_local_read_domain_and_checks_stale_claim(self):
        e = status(mode="PERIODIC", state="OK", age=15001)
        e["time"]["event_clock_domain_id"] = "SYN_FOREIGN_SOURCE_CLOCK"
        self.assertEqual(play(e)["sources"][0]["status"], "STALE")
        for ms in [None, 0, 15000]:
            r = play(status(mode="PERIODIC", state="STALE", age=ms))
            self.assertEqual(r["sources"][0]["status"], "UNKNOWN")
        self.assertEqual(play(status(mode="PERIODIC", state="STALE", age=15001))["sources"][0]["status"], "STALE")
        r = play(status(), status(seq=1, mode="PERIODIC", state="OK"))
        self.assertEqual(r["sources"][0]["status"], "CONFLICT")

    def test_conflicted_terminal_is_quarantined_and_unknown(self):
        for a, b in [(exited(seq=0), exited(seq=0, code=7)),
                     (terminal(seq=0), terminal(seq=0, outcome="FAILED"))]:
            r = play(a, b)
            self.assertEqual([e["type"] for e in r["events"]], ["CONFLICT_EVENT"])
            self.assertNotIn("record", r["events"][0])
            self.assertEqual(r["runs"][0]["lifecycle"], "UNKNOWN")
            self.assertEqual(r["sources"][0]["status"], "CONFLICT")
            self.assertEqual(r["exits"], [])

    def test_manifest_binding_cannot_silently_change_gpu_or_rank(self):
        for field, value in [("gpu_uuids", ["SYN_GPU_OTHER"]), ("local_rank", 1), ("start_ticks_hz", 200)]:
            r = play(manifest(), exited(ident=identity(**{field: value})))
            self.assertEqual(r["attempts"][0]["lifecycle"], "UNKNOWN", field)
        r = play(manifest(), manifest(seq=1, members=[identity(process_start_ticks=999)]), exited(seq=2))
        self.assertEqual(r["attempts"][0]["lifecycle"], "UNKNOWN")

    def test_complete_two_members_and_failure_are_exact(self):
        a = identity(world_size=2)
        b = identity(world_size=2, rank=1, local_rank=1, pid=101, gpu_uuids=["SYN_GPU_B"])
        r = play(manifest(ident=a, members=[a, b]), exited(ident=a), exited(seq=2, ident=b))
        self.assertEqual(r["attempts"][0]["lifecycle"], "ATTEMPT_EXITED_OK")
        self.assertEqual(r["attempts"][0]["terminated_members"], 2)
        self.assertEqual(r["runs"][0]["lifecycle"], "UNKNOWN")
        r = play(manifest(ident=a, members=[a, b]), exited(ident=a), exited(seq=2, ident=b, code=7))
        self.assertEqual(r["attempts"][0]["lifecycle"], "ATTEMPT_EXITED_WITH_FAILURE")
        self.assertEqual(r["runs"][0]["lifecycle"], "UNKNOWN")

    def test_no_restart_proof_contradicted_by_later_attempt(self):
        r = play(manifest(), exited(), terminal(proof="FINAL_ATTEMPT", final="SYN_ATTEMPT_0", no_restart=True),
                 event(seq=3, ident=identity(attempt_id="SYN_ATTEMPT_1")))
        self.assertEqual(r["runs"][0]["lifecycle"], "UNKNOWN")
        self.assertEqual(r["attempts"][1]["lifecycle"], "UNKNOWN")

    def test_incomplete_final_proof_and_unknown_outcome_are_not_null_lifecycle(self):
        t = terminal(seq=0)
        t["payload"]["outcome"] = None
        t["unknown_reasons"]["payload.outcome"] = "not_supplied"
        r = play(t)
        self.assertEqual(r["runs"][0]["lifecycle"], "UNKNOWN")
        r = play(manifest(), exited(), terminal(proof="FINAL_ATTEMPT", final="SYN_MISSING", no_restart=True))
        self.assertEqual(r["runs"][0]["lifecycle"], "UNKNOWN")

    def test_historical_exit_survives_reader_failure_no_new_exit_inferred(self):
        r = play(exited(seq=0), status(seq=1, state="UNAVAILABLE", read="UNAVAILABLE"))
        self.assertEqual(r["processes"][0]["lifecycle"], "EXITED_OK")
        self.assertEqual(r["processes"][0]["coverage_status"], "UNKNOWN")
        self.assertEqual(len(r["exits"]), 1)
        r = play(event(seq=0, payload=dict(process_presence="NOT_OBSERVED", device_samples=[], progress=None)))
        self.assertEqual(r["exits"], [])
        self.assertEqual(r["processes"][0]["lifecycle"], "UNKNOWN")

    def test_source_epoch_scopes_dedup_and_does_not_silently_fill_old_gap(self):
        a, b = status(seq=0), status(seq=2)
        c = status(seq=0)
        c["source_epoch"] = "SYN_EPOCH_1"
        r = play(a, b, c)
        self.assertEqual(r["counts"]["accepted"], 3)
        self.assertEqual([s["status"] for s in r["sources"]], ["GAP", "IDLE"])
        self.assertEqual(r["runs"][0]["coverage_status"], "UNKNOWN")

    def test_no_time_arithmetic_across_domains_or_huge_integers(self):
        e = status(mode="PERIODIC", state="OK", age=15001)
        e["time"]["observed_clock_domain_id"] = None
        e["unknown_reasons"]["time.observed_clock_domain_id"] = "not_supplied"
        r = play(e)
        self.assertEqual(r["sources"][0]["status"], "UNKNOWN")
        self.assertIsNone(r["sources"][0]["last_record_age_ms"])
        for field in ["event_monotonic_ns", "observed_monotonic_ns"]:
            e = event()
            e["time"][field] = 10**1000
            r = play(e)
            self.assertIsNone(r["processes"][0]["last_observed_age_ms"])
        r = play(status(mode="PERIODIC", state="OK", age=10**1000))
        self.assertEqual(r["sources"][0]["status"], "UNKNOWN")

    def test_invalid_json_types_and_duplicate_keys_do_not_stop_next_line(self):
        for raw in [b'{"x":1,"x":2}\n', b'NaN\n', b'[]\n', b'null\n',
                    b'"text"\n', b'\xff\n', b'[' * 1500 + b'0' + b']' * 1500 + b'\n']:
            r = play(raw, event(seq=1))
            self.assertEqual(r["counts"]["invalid"], 1)
            self.assertEqual(r["counts"]["accepted"], 1)
        for field, value in [("source_seq", True), ("source_seq", -1), ("event_type", "UNKNOWN")]:
            e = event()
            e[field] = value
            self.assertEqual(play(e)["events"], [])

    def test_exact_line_limit_and_output_write_errors(self):
        raw = line(event())
        exact = raw[:-1] + b" " * (MAX_LINE_BYTES - len(raw)) + b"\n"
        self.assertEqual(len(exact), MAX_LINE_BYTES)
        self.assertEqual(replay([exact])["counts"]["accepted"], 1)
        self.assertEqual(replay([exact[:-1] + b" \n"])["diagnostics"][0]["code"], "LINE_LIMIT")
        with patch("observatory.__main__.MAX_OUTPUT_BYTES", 1):
            out, err = io.StringIO(), io.StringIO()
            self.assertEqual(run(io.BytesIO(raw), out, err), 2)
            self.assertEqual(err.getvalue(), "OUTPUT_LIMIT\n")
            self.assertEqual(out.getvalue(), "")
        class Unavailable(io.StringIO):
            def write(self, value):
                raise OSError("private input must never appear")
        err = io.StringIO()
        self.assertEqual(run(io.BytesIO(raw), Unavailable(), err), 2)
        self.assertEqual(err.getvalue(), "OUTPUT_UNAVAILABLE\n")

    def test_malformed_record_cannot_contaminate_lifecycle_or_leak_payload(self):
        bad = exited(seq=1, code=7)
        bad["identity"]["pid"] = True
        bad["payload"]["password"] = "sensitive_example"
        r = play(exited(seq=0), bad, event(seq=2))
        self.assertEqual(r["counts"]["invalid"], 1)
        self.assertEqual(r["exits"][0]["lifecycle"], "EXITED_OK")
        self.assertEqual(r["processes"][0]["coverage_status"], "UNKNOWN")
        self.assertNotIn("sensitive_example", canonical(r))


if __name__ == "__main__":
    unittest.main()
