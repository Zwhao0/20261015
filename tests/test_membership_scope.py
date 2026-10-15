"""R1: local identities cannot establish complete Attempt membership."""

import copy
import unittest
from unittest.mock import patch

from observatory.contract import InvalidRecord, validate_record
from observatory.engine import replay
from tests.builders import event, exited, identity, line, manifest, terminal


def local_identity(scope, complete=True):
    return event("IDENTITY", seq=0, ident=identity(scope=scope),
                 payload={"scope": scope, "members": [identity()],
                          "membership_complete": complete})


def replay_claim(record, with_final_proof):
    records = [record, exited(seq=1)]
    if with_final_proof:
        records.append(terminal(seq=2, proof="FINAL_ATTEMPT",
                                final="SYN_ATTEMPT_0", no_restart=True))
    return replay([line(r) for r in records])


class MembershipScopeTests(unittest.TestCase):
    def assert_local_claim_stays_unknown(self, scope):
        for proof in [False, True]:
            with self.subTest(scope=scope, final_proof=proof):
                result = replay_claim(local_identity(scope), proof)
                self.assertEqual(
                    (result["attempts"][0]["lifecycle"], result["runs"][0]["lifecycle"]),
                    ("UNKNOWN", "UNKNOWN"),
                )
                self.assertEqual(result["counts"]["invalid"], 1)
                self.assertEqual([d["code"] for d in result["diagnostics"]], ["INVALID_RECORD"])
                self.assertEqual(len(result["exits"]), 1)
                self.assertEqual(result["exits"][0]["lifecycle"], "EXITED_OK")
                self.assertEqual(result["attempts"][0]["known_members"], 1)
                self.assertIsNone(result["attempts"][0]["expected_members"])
                self.assertIsNone(result["runs"][0]["terminal_evidence_ref"])

    def test_worker_complete_claim_cannot_complete_attempt_or_run(self):
        self.assert_local_claim_stays_unknown("worker")

    def test_launcher_complete_claim_cannot_complete_attempt_or_run(self):
        self.assert_local_claim_stays_unknown("launcher")

    def test_run_complete_claim_cannot_complete_attempt_or_run(self):
        self.assert_local_claim_stays_unknown("run")

    def test_contract_rejects_non_attempt_complete_claims(self):
        for scope in ["worker", "launcher", "run"]:
            with self.subTest(scope=scope):
                with self.assertRaisesRegex(InvalidRecord, "complete membership requires attempt scope"):
                    validate_record(local_identity(scope))

    def test_contract_complete_members_are_workers(self):
        for scope in ["launcher", "attempt", "run"]:
            with self.subTest(member_scope=scope):
                record = manifest(members=[identity(scope=scope)])
                with self.assertRaisesRegex(InvalidRecord, "complete membership requires worker members"):
                    validate_record(record)

    def test_partial_local_identities_do_not_complete_attempt(self):
        for scope in ["worker", "launcher", "run"]:
            with self.subTest(scope=scope):
                record = local_identity(scope, complete=False)
                self.assertFalse(validate_record(record)["payload"]["membership_complete"])
                result = replay_claim(record, True)
                self.assertEqual(result["counts"]["invalid"], 0)
                self.assertEqual(result["attempts"][0]["lifecycle"], "UNKNOWN")
                self.assertEqual(result["runs"][0]["lifecycle"], "UNKNOWN")

    def test_legal_attempt_manifest_can_support_final_proof(self):
        for proof, expected_run in [(False, "UNKNOWN"), (True, "COMPLETED")]:
            with self.subTest(final_proof=proof):
                result = replay_claim(manifest(), proof)
                self.assertEqual(result["counts"]["invalid"], 0)
                self.assertEqual(result["attempts"][0]["lifecycle"], "ATTEMPT_EXITED_OK")
                self.assertEqual(result["runs"][0]["lifecycle"], expected_run)

    def test_aggregator_checks_scope_even_if_validation_is_bypassed(self):
        # Inject an already parsed local IDENTITY to exercise the second boundary.
        def relaxed_identity_validator(record):
            return copy.deepcopy(record) if record["event_type"] == "IDENTITY" else validate_record(record)
        for scope in ["worker", "launcher", "run"]:
            for proof in [False, True]:
                with self.subTest(scope=scope, final_proof=proof):
                    with patch("observatory.engine.validate_record", side_effect=relaxed_identity_validator):
                        result = replay_claim(local_identity(scope), proof)
                    self.assertEqual(result["counts"]["invalid"], 0)
                    self.assertEqual(
                        (result["attempts"][0]["lifecycle"], result["runs"][0]["lifecycle"]),
                        ("UNKNOWN", "UNKNOWN"),
                    )
                    self.assertEqual(len(result["exits"]), 1)


if __name__ == "__main__":
    unittest.main()
