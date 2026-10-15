import unittest

from observatory.contract import InvalidRecord, validate_record


def identity(scope="worker"):
    return {
        "scope": scope,
        "job_id": "SYN_JOB_A",
        "run_id": "SYN_RUN_A",
        "attempt_id": "SYN_ATTEMPT_A",
        "world_size": 1,
        "rank": 0,
        "local_rank": 0,
        "host_id": "SYN_HOST_A",
        "boot_id": "SYN_BOOT_A",
        "pid_namespace_id": "SYN_NS_A",
        "pid": 101,
        "process_start_ticks": 2048,
        "start_ticks_hz": 100,
        "gpu_uuids": ["SYN_GPU_A"],
    }


def record(event_type, payload, *, scope="worker"):
    return {
        "schema_version": "0.1",
        "event_id": "SYN_EVENT_A",
        "event_type": event_type,
        "source_id": "SYN_SOURCE_A",
        "source_epoch": "SYN_EPOCH_A",
        "source_seq": 0,
        "origin": "SYNTHETIC",
        "identity": identity(scope),
        "time": {
            "event_time_utc": "2026-10-15T10:00:00Z",
            "observed_time_utc": "2026-10-15T10:00:01.125Z",
            "event_monotonic_ns": 10,
            "observed_monotonic_ns": 11,
            "event_clock_domain_id": "SYN_CLOCK_A",
            "observed_clock_domain_id": "SYN_CLOCK_A",
            "uncertainty_ms": 0,
        },
        "payload": payload,
        "evidence_ref": "SYN_EVIDENCE_A",
        "unknown_reasons": {},
        "source_cursor": "SYN_CURSOR_A",
        "content_sha256": "a" * 64,
    }


class ValidateRecordTests(unittest.TestCase):
    def test_process_exit_posix_wait_is_decoded_and_copy_is_independent(self):
        source = record(
            "PROCESS_EXIT",
            {
                "scope": "worker",
                "authority": "parent_wait",
                "status_kind": "EXITED",
                "raw_status": 1792,
                "raw_status_format": "posix_wait",
                "exit_code": 7,
                "signal": None,
                "expected_stop": False,
            },
        )
        source["unknown_reasons"] = {"payload.signal": "not a signaled exit"}
        normalized = validate_record(source)
        self.assertEqual(normalized["payload"]["exit_code"], 7)
        self.assertIsNone(normalized["payload"]["signal"])
        self.assertIsNot(normalized, source)
        normalized["identity"]["job_id"] = "SYN_JOB_CHANGED"
        self.assertEqual(source["identity"]["job_id"], "SYN_JOB_A")

    def test_subprocess_negative_returncode_is_signal(self):
        source = record(
            "PROCESS_EXIT",
            {
                "scope": "worker",
                "authority": "parent_wait",
                "status_kind": "SIGNALED",
                "raw_status": -15,
                "raw_status_format": "subprocess_returncode",
                "exit_code": None,
                "signal": 15,
                "expected_stop": None,
            },
        )
        source["unknown_reasons"] = {
            "payload.exit_code": "signal exit",
            "payload.expected_stop": "intent unavailable",
        }
        self.assertEqual(validate_record(source)["payload"]["signal"], 15)

    def test_unverified_shell_code_stays_unknown(self):
        source = record(
            "PROCESS_EXIT",
            {
                "scope": "worker",
                "authority": "log_unverified",
                "status_kind": "UNKNOWN",
                "raw_status": 137,
                "raw_status_format": "shell_unverified",
                "exit_code": None,
                "signal": None,
                "expected_stop": None,
            },
        )
        source["unknown_reasons"] = {
            "payload.exit_code": "encoding unverified",
            "payload.signal": "encoding unverified",
            "payload.expected_stop": "intent unavailable",
        }
        self.assertEqual(validate_record(source)["payload"]["status_kind"], "UNKNOWN")

    def test_exit_declaration_must_match_raw_encoding(self):
        source = record(
            "PROCESS_EXIT",
            {
                "scope": "worker",
                "authority": "parent_wait",
                "status_kind": "EXITED",
                "raw_status": 1792,
                "raw_status_format": "posix_wait",
                "exit_code": 6,
                "signal": None,
                "expected_stop": False,
            },
        )
        source["unknown_reasons"] = {"payload.signal": "not a signaled exit"}
        with self.assertRaisesRegex(InvalidRecord, "termination fields do not match raw encoding"):
            validate_record(source)

    def test_invalid_utc_is_downgraded_with_reason(self):
        source = record("SNAPSHOT", {"process_presence": "UNKNOWN", "device_samples": [], "progress": {"step": 4, "semantics": "global_step", "source_id": "SYN_SOURCE_A"}})
        source["time"]["event_time_utc"] = "not-a-time"
        normalized = validate_record(source)
        self.assertIsNone(normalized["time"]["event_time_utc"])
        self.assertEqual(
            normalized["unknown_reasons"]["time.event_time_utc"],
            "invalid UTC timestamp",
        )
        self.assertEqual(source["time"]["event_time_utc"], "not-a-time")

    def test_metric_error_and_sentinel_are_normalized(self):
        source = record(
            "SNAPSHOT",
            {
                "process_presence": "OBSERVED",
                "device_samples": [
                    {
                        "gpu_uuid": "SYN_GPU_A",
                        "metrics": {
                            "memory_used": {"value": 123, "unit": "bytes", "status": "ERROR"},
                            "utilization": {"value": -1, "unit": "percent", "status": "OK"},
                        },
                    }
                ],
                "progress": None,
            },
        )
        source["unknown_reasons"] = {"payload.progress": "no progress sample"}
        normalized = validate_record(source)
        metrics = normalized["payload"]["device_samples"][0]["metrics"]
        self.assertIsNone(metrics["memory_used"]["value"])
        self.assertIsNone(metrics["utilization"]["value"])
        self.assertEqual(metrics["utilization"]["status"], "UNKNOWN")
        self.assertIn("payload.device_samples[0].metrics.memory_used.value", normalized["unknown_reasons"])
        self.assertIn("payload.device_samples[0].metrics.utilization.value", normalized["unknown_reasons"])
        self.assertIsNone(normalized["payload"]["progress"])

    def test_null_requires_reason_and_partial_identity_is_allowed(self):
        source = record("IDENTITY", {"scope": "worker", "members": [], "membership_complete": False})
        source["identity"]["attempt_id"] = None
        source["payload"]["scope"] = "worker"
        source["unknown_reasons"] = {"identity.attempt_id": "attempt not known"}
        self.assertIsNone(validate_record(source)["identity"]["attempt_id"])

        del source["unknown_reasons"]["identity.attempt_id"]
        with self.assertRaisesRegex(InvalidRecord, "null value lacks a reason"):
            validate_record(source)

    def test_source_status_contract_and_cross_source_rejection(self):
        source = record(
            "SOURCE_STATUS",
            {
                "source_mode": "EVENT_DRIVEN",
                "expected_interval_ms": None,
                "freshness_timeout_ms": None,
                "last_successful_read_monotonic_ns": 100,
                "last_record_age_ms": 3600000,
                "status": "IDLE",
                "read_status": "OK",
                "reason": "read succeeded with no new event",
                "affected_source_id": "SYN_SOURCE_A",
            },
        )
        source["unknown_reasons"] = {
            "payload.expected_interval_ms": "event-driven source",
            "payload.freshness_timeout_ms": "event-driven source",
        }
        self.assertEqual(validate_record(source)["payload"]["status"], "IDLE")
        source["payload"]["affected_source_id"] = "SYN_SOURCE_B"
        with self.assertRaisesRegex(InvalidRecord, "affected source must match record source"):
            validate_record(source)

    def test_run_terminal_partial_proof_can_remain_unknown(self):
        source = record(
            "RUN_TERMINAL",
            {
                "scope": "run",
                "authority": "UNKNOWN",
                "proof_kind": None,
                "outcome": None,
                "final_attempt_id": None,
                "no_restart_or_resume": None,
            },
            scope="run",
        )
        source["unknown_reasons"] = {
            "payload.proof_kind": "proof unavailable",
            "payload.outcome": "outcome unavailable",
            "payload.final_attempt_id": "final attempt unavailable",
            "payload.no_restart_or_resume": "restart policy unavailable",
        }
        self.assertIsNone(validate_record(source)["payload"]["outcome"])

    def test_run_outcome_requires_matching_authoritative_proof(self):
        source = record(
            "RUN_TERMINAL",
            {
                "scope": "run",
                "authority": "UNKNOWN",
                "proof_kind": "RUN_TERMINAL",
                "outcome": "COMPLETED",
                "final_attempt_id": None,
                "no_restart_or_resume": None,
            },
            scope="run",
        )
        source["unknown_reasons"] = {
            "payload.final_attempt_id": "not applicable",
            "payload.no_restart_or_resume": "not applicable",
        }
        with self.assertRaisesRegex(InvalidRecord, "authoritative RUN_TERMINAL proof"):
            validate_record(source)

    def test_schema_version_required_and_exact(self):
        source = record("SNAPSHOT", {"process_presence": "UNKNOWN", "device_samples": [], "progress": None})
        source["unknown_reasons"] = {"payload.progress": "no progress sample"}
        del source["schema_version"]
        with self.assertRaisesRegex(InvalidRecord, "schema_version.*missing required field"):
            validate_record(source)

        source = record("SNAPSHOT", {"process_presence": "UNKNOWN", "device_samples": [], "progress": None})
        source["unknown_reasons"] = {"payload.progress": "no progress sample"}
        source["schema_version"] = 0.1
        with self.assertRaisesRegex(InvalidRecord, "unsupported schema version"):
            validate_record(source)

    def test_zero_null_and_large_sequence_are_distinct(self):
        source = record("IDENTITY", {"scope": "worker", "members": [], "membership_complete": False})
        source["source_seq"] = 10**200
        source["identity"]["rank"] = None
        source["unknown_reasons"] = {"identity.rank": "rank unavailable"}
        normalized = validate_record(source)
        self.assertEqual(normalized["source_seq"], 10**200)
        self.assertIsNone(normalized["identity"]["rank"])

        source["identity"]["rank"] = 0
        source["unknown_reasons"] = {}
        self.assertEqual(validate_record(source)["identity"]["rank"], 0)

    def test_real_origin_is_rejected_without_echoing_record_values(self):
        source = record("SNAPSHOT", {"process_presence": "UNKNOWN", "device_samples": [], "progress": None})
        source["origin"] = "REAL"
        source["unknown_reasons"] = {"payload.progress": "no progress sample"}
        source["identity"]["job_id"] = "/private/real-job"
        with self.assertRaises(InvalidRecord) as raised:
            validate_record(source)
        self.assertIn("offline export safety gate", str(raised.exception))
        self.assertNotIn("/private/real-job", str(raised.exception))

    def test_unknown_fields_and_nonfinite_or_boolean_numbers_are_rejected(self):
        source = record("SNAPSHOT", {"process_presence": "UNKNOWN", "device_samples": [], "progress": None})
        source["unknown_reasons"] = {"payload.progress": "no progress sample"}
        source["payload"]["private/path"] = "secret"
        with self.assertRaisesRegex(InvalidRecord, "unexpected field") as raised:
            validate_record(source)
        self.assertNotIn("private/path", str(raised.exception))

        source = record("SNAPSHOT", {"process_presence": "UNKNOWN", "device_samples": [], "progress": None})
        source["unknown_reasons"] = {"payload.progress": "no progress sample"}
        source["time"]["uncertainty_ms"] = float("nan")
        with self.assertRaisesRegex(InvalidRecord, "finite number"):
            validate_record(source)

        source = record("IDENTITY", {"scope": "worker", "members": [], "membership_complete": False})
        source["identity"]["rank"] = True
        with self.assertRaisesRegex(InvalidRecord, "integer in range"):
            validate_record(source)

    def test_evidence_reference_must_be_logical_and_synthetic(self):
        source = record("SNAPSHOT", {"process_presence": "UNKNOWN", "device_samples": [], "progress": None})
        source["unknown_reasons"] = {"payload.progress": "no progress sample"}
        source["evidence_ref"] = "/var/log/private.jsonl"
        with self.assertRaises(InvalidRecord) as raised:
            validate_record(source)
        self.assertNotIn("/var/log/private.jsonl", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
