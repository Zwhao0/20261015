"""Independent semantic assertions for public synthetic sidecars; no live I/O."""

import copy
import hashlib
import json
from pathlib import Path
import unittest

from observatory.parallel_context import InvalidContext, normalize_contexts, validate_context


ROOT = Path(__file__).parent / "fixtures" / "parallel_context"


def fixture(name="mixed"):
    return json.loads((ROOT / (name + ".json")).read_text())


def unknown(reason="NO_SOURCE"):
    return {"value": None, "evidence": [], "unknown_reason": reason}


class ParallelContextTests(unittest.TestCase):
    def assertInvalid(self, value):
        with self.assertRaises(InvalidContext):
            validate_context(value)

    def test_dp_only_explicit_members(self):
        result = validate_context(fixture("dp_only"))
        self.assertEqual([g["member_ids"] for g in result["groups"]["value"]],
                         [["SYN_W0", "SYN_W2"], ["SYN_W1", "SYN_W3"]])
        self.assertEqual(result["experts"]["value"], [])

    def test_mixed_intersecting_non_cartesian_groups(self):
        result = validate_context(fixture())
        groups = result["groups"]["value"]
        self.assertEqual({g["group_type"] for g in groups}, {"DP", "TP", "PP", "EP"})
        ep = [g for g in groups if g["group_type"] == "EP"]
        self.assertEqual([len(g["member_ids"]) for g in ep], [3, 2])
        self.assertEqual(set(ep[0]["member_ids"]) & set(ep[1]["member_ids"]), {"SYN_W3"})

    def test_group_rank_order_is_not_global_rank_or_gpu(self):
        result = validate_context(fixture())
        tp = result["groups"]["value"][2]
        self.assertEqual(tp["member_ids"], ["SYN_W1", "SYN_W0"])
        workers = {m["worker_id"]: m for m in result["members"]["value"]}
        self.assertEqual([workers[w]["global_rank"]["value"] for w in tp["member_ids"]], [2, 7])
        self.assertEqual(workers["SYN_W1"]["gpu_ids"]["value"], ["SYN_GPU_8"])

    def test_static_expert_replica_is_separate_from_routing(self):
        result = validate_context(fixture())
        experts = result["experts"]["value"]
        self.assertEqual([(e["expert_id"], e["replica_id"]) for e in experts],
                         [("SYN_E0", "SYN_R0"), ("SYN_E0", "SYN_R1"), ("SYN_E1", "SYN_R0")])
        self.assertEqual(experts[0]["owner_worker_ids"], ["SYN_W0"])
        self.assertIsNone(result["routing"]["token_routing"]["value"])
        self.assertIsNone(result["routing"]["expert_load"]["value"])

    def test_missing_rank_gpu_and_expert_group_remain_unknown(self):
        result = normalize_contexts([fixture("missing_mapping")])
        self.assertEqual(result["status"], "UNKNOWN")
        context = result["contexts"][0]["context"]
        self.assertIsNone(context["members"]["value"][0]["global_rank"]["value"])
        self.assertIsNone(context["members"]["value"][0]["gpu_ids"]["value"])
        self.assertIsNone(context["experts"]["value"][0]["communication_group_ids"]["value"])
        self.assertIn("members.value[0].gpu_ids", result["contexts"][0]["unknown_paths"])

    def test_no_sources_no_fake_precision(self):
        result = normalize_contexts([fixture("unknown")])
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual(result["diagnostics"], [])
        self.assertIsNone(result["contexts"][0]["context"]["members"]["value"])

    def test_missing_evidence_rejects_concrete_values(self):
        for field in ("membership_epoch", "topology_epoch", "members", "groups", "experts"):
            with self.subTest(field=field):
                context = fixture()
                context[field]["evidence"] = []
                self.assertInvalid(context)

    def test_unverified_log_cannot_support_identity(self):
        for kind in ("LOG_UNVERIFIED", "UNKNOWN", "DEVICE_MONITOR"):
            with self.subTest(kind=kind):
                context = fixture()
                context["evidence"][0]["kind"] = kind
                self.assertInvalid(context)

    def test_scope_mismatch_is_rejected(self):
        context = fixture()
        context["evidence"][0]["scope"]["attempt_id"] = "SYN_OTHER"
        self.assertInvalid(context)

    def test_invalid_member_fixture_is_rejected(self):
        result = normalize_contexts([fixture("invalid_member"), fixture("dp_only")])
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual([x["index"] for x in result["contexts"]], [1])
        self.assertEqual(result["diagnostics"][0]["code"], "INVALID_CONTEXT")
        self.assertNotIn("SYN_MISSING", json.dumps(result["diagnostics"]))

    def test_duplicate_group_or_member_is_rejected(self):
        for field in ("groups", "members", "experts"):
            with self.subTest(field=field):
                context = fixture()
                context[field]["value"].append(copy.deepcopy(context[field]["value"][0]))
                self.assertInvalid(context)

    def test_duplicate_member_within_group_is_rejected(self):
        context = fixture()
        group = context["groups"]["value"][0]
        group["member_ids"].append(group["member_ids"][0])
        self.assertInvalid(context)

    def test_wrong_group_epoch_is_rejected(self):
        for field in ("membership_epoch", "topology_epoch"):
            with self.subTest(field=field):
                context = fixture()
                context["groups"]["value"][0][field] = 1
                self.assertInvalid(context)

    def test_unknown_epoch_cannot_support_precise_members_or_groups(self):
        for field in ("membership_epoch", "topology_epoch"):
            with self.subTest(field=field):
                context = fixture()
                context[field] = unknown("EPOCH_UNKNOWN")
                self.assertInvalid(context)

    def test_rejoin_new_epochs_keeps_both_process_instances(self):
        result = normalize_contexts([fixture(), fixture("rejoined")])
        self.assertEqual(result["diagnostics"], [])
        self.assertEqual(result["status"], "SYNTHETIC_SUPPORTED")
        self.assertEqual([x["context"]["members"]["value"][0]["process"]["value"]["process_start_ticks"]
                          for x in result["contexts"]], [1000, 2000])

    def test_membership_epoch_conflict_isolates_all_versions(self):
        original, changed = fixture(), fixture()
        changed["members"]["value"][0]["process"]["value"]["process_start_ticks"] = 2000
        result = normalize_contexts([original, changed])
        self.assertEqual(result["contexts"], [])
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual(result["diagnostics"][0]["code"], "MEMBERSHIP_CONFLICT")
        self.assertEqual(result["diagnostics"][0]["indices"], [0, 1])

    def test_topology_epoch_conflict_no_first_wins(self):
        original, changed = fixture(), fixture()
        changed["groups"]["value"][0]["member_ids"].reverse()
        for records in ([original, changed], [changed, original]):
            result = normalize_contexts(records)
            self.assertEqual(result["contexts"], [])
            self.assertEqual(result["diagnostics"][0]["code"], "TOPOLOGY_CONFLICT")

    def test_resize_cannot_reuse_topology_epoch(self):
        changed = fixture("rejoined")
        changed["topology_epoch"]["value"] = 0
        for group in changed["groups"]["value"]:
            group["topology_epoch"] = 0
        result = normalize_contexts([fixture(), changed])
        self.assertEqual(result["contexts"], [])
        self.assertIn("TOPOLOGY_CONFLICT", [x["code"] for x in result["diagnostics"]])

    def test_attempt_partition_does_not_inherit_epochs_or_process_state(self):
        context = fixture()
        context["scope"]["attempt_id"] = "SYN_ATTEMPT_1"
        for ev in context["evidence"]:
            ev["scope"]["attempt_id"] = "SYN_ATTEMPT_1"
        context["members"]["value"][0]["global_rank"]["value"] = 3
        result = normalize_contexts([fixture(), context])
        self.assertEqual(len(result["contexts"]), 2)
        self.assertEqual(result["diagnostics"], [])
        self.assertNotIn("exit", json.dumps(result).lower())

    def test_source_slot_conflict_isolates_both(self):
        changed = fixture()
        changed["evidence"][0]["content_sha256"] = "b" * 64
        result = normalize_contexts([fixture(), changed])
        self.assertEqual(result["contexts"], [])
        self.assertEqual([d["code"] for d in result["diagnostics"]], ["SOURCE_CONFLICT"])

    def test_source_epoch_change_is_separate(self):
        changed = fixture()
        changed["evidence"][0]["source_epoch"] = "SYN_SOURCE_EPOCH_2"
        changed["evidence"][0]["content_sha256"] = "b" * 64
        result = normalize_contexts([fixture(), changed])
        self.assertEqual(len(result["contexts"]), 2)
        self.assertEqual(result["diagnostics"], [])

    def test_exact_duplicate_only_counted_once(self):
        result = normalize_contexts([fixture(), fixture()])
        self.assertEqual(result["duplicates"], 1)
        self.assertEqual(len(result["contexts"]), 1)
        self.assertEqual(result["diagnostics"], [])

    def test_static_expert_different_in_same_epoch_conflicts(self):
        changed = fixture()
        changed["experts"]["value"][0]["owner_worker_ids"] = ["SYN_W1"]
        result = normalize_contexts([fixture(), changed])
        self.assertEqual(result["contexts"], [])
        self.assertIn("TOPOLOGY_CONFLICT", [d["code"] for d in result["diagnostics"]])

    def test_expert_owner_must_be_member_and_in_ep_group(self):
        for owner in ("SYN_MISSING", "SYN_W2"):
            with self.subTest(owner=owner):
                context = fixture()
                context["experts"]["value"][0]["owner_worker_ids"] = [owner]
                self.assertInvalid(context)

    def test_expert_cannot_use_dp_group(self):
        context = fixture()
        context["experts"]["value"][0]["communication_group_ids"]["value"] = ["SYN_DP0"]
        self.assertInvalid(context)

    def test_dynamic_routing_or_load_cannot_be_fabricated(self):
        for field in ("token_routing", "expert_load"):
            with self.subTest(field=field):
                context = fixture()
                context["routing"][field] = {"value": [], "evidence": ["SYN_EV_E"], "unknown_reason": None}
                self.assertInvalid(context)

    def test_partial_process_instance_is_rejected(self):
        context = fixture()
        del context["members"]["value"][0]["process"]["value"]["boot_id"]
        self.assertInvalid(context)

    def test_process_mapping_missing_remains_unknown(self):
        context = fixture()
        context["members"]["value"][0]["process"] = unknown("MISSING_MAPPING")
        result = normalize_contexts([context])
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertIsNone(result["contexts"][0]["context"]["members"]["value"][0]["process"]["value"])

    def test_same_process_cannot_map_two_workers_even_different_tick_frequency(self):
        context = fixture()
        other = copy.deepcopy(context["members"]["value"][0]["process"])
        other["value"]["start_ticks_hz"] = 200
        context["members"]["value"][1]["process"] = other
        self.assertInvalid(context)

    def test_duplicate_global_and_local_rank_rejected(self):
        for field in ("global_rank", "local_rank"):
            with self.subTest(field=field):
                context = fixture()
                context["members"]["value"][1][field] = copy.deepcopy(context["members"]["value"][0][field])
                self.assertInvalid(context)

    def test_real_unknown_fields_bool_bad_version_and_identifier_rejected(self):
        for change in ({"origin": "REAL"}, {"context_version": "0.2"}, {"extra": 1}):
            with self.subTest(change=change):
                context = fixture()
                context.update(change)
                self.assertInvalid(context)
        context = fixture()
        context["membership_epoch"]["value"] = True
        self.assertInvalid(context)
        context = fixture()
        context["scope"]["job_id"] = "/private/input"
        self.assertInvalid(context)

    def test_bounds_and_empty_batch(self):
        with self.assertRaises(InvalidContext):
            normalize_contexts([fixture()] * 129)
        self.assertEqual(normalize_contexts([])["status"], "UNKNOWN")
        context = fixture()
        context["members"]["value"] *= 65
        self.assertInvalid(context)

    def test_unknown_claim_requires_explicit_reason_and_no_precision(self):
        for change in ({"unknown_reason": None}, {"evidence": ["SYN_EV_L"]}):
            context = fixture("unknown")
            context["members"].update(change)
            self.assertInvalid(context)

    def test_normalization_does_not_mutate_or_alias_input(self):
        source = fixture()
        original = copy.deepcopy(source)
        result = normalize_contexts([source])
        self.assertEqual(source, original)
        result["contexts"][0]["context"]["scope"]["job_id"] = "SYN_CHANGED"
        self.assertEqual(source, original)

    def test_optional_group_types_keep_explicit_members(self):
        context = fixture()
        for group, kind in zip(context["groups"]["value"],
                               ("CP", "VIRTUAL_PP", "EXPERT_TENSOR")):
            group["group_type"] = kind
        result = validate_context(context)
        self.assertEqual(result["groups"]["value"][0]["member_ids"], ["SYN_W0", "SYN_W2"])
        self.assertEqual(result["groups"]["value"][2]["group_type"], "EXPERT_TENSOR")

    def test_elastic_resize_explicit_new_members_and_groups(self):
        context = fixture("rejoined")
        context["members"]["value"] = context["members"]["value"][:3]
        context["groups"]["value"] = context["groups"]["value"][:1]
        context["experts"]["value"] = []
        result = normalize_contexts([fixture(), context])
        self.assertEqual(result["diagnostics"], [])
        self.assertEqual([len(x["context"]["members"]["value"]) for x in result["contexts"]], [4, 3])
        self.assertEqual(result["contexts"][1]["context"]["groups"]["value"][0]["member_ids"], ["SYN_W0", "SYN_W2"])

    def test_gpu_unknown_differs_from_evidenced_no_gpu(self):
        context = fixture()
        context["members"]["value"][0]["gpu_ids"]["value"] = []
        result = normalize_contexts([context])
        self.assertEqual(result["status"], "SYNTHETIC_SUPPORTED")
        self.assertEqual(result["contexts"][0]["context"]["members"]["value"][0]["gpu_ids"]["value"], [])

    def test_duplicate_evidence_and_wrong_reference_rejected(self):
        context = fixture()
        context["evidence"].append(copy.deepcopy(context["evidence"][0]))
        self.assertInvalid(context)
        context = fixture()
        context["groups"]["value"][0]["evidence"] = ["SYN_MISSING"]
        self.assertInvalid(context)

    def test_empty_members_or_empty_group_rejected(self):
        context = fixture()
        context["members"]["value"] = []
        self.assertInvalid(context)
        context = fixture()
        context["groups"]["value"][0]["member_ids"] = []
        self.assertInvalid(context)

    def test_partial_epoch_data_does_not_enrich_other_context(self):
        result = normalize_contexts([fixture("unknown"), fixture()])
        self.assertEqual(len(result["contexts"]), 2)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertIsNone(result["contexts"][0]["context"]["membership_epoch"]["value"])
        self.assertIsNone(result["contexts"][0]["context"]["members"]["value"])

    def test_pure_deterministic_result_and_routing_unknown_paths(self):
        first = normalize_contexts([fixture()])
        second = normalize_contexts([fixture()])
        self.assertEqual(first, second)
        self.assertEqual(first["contexts"][0]["unknown_paths"],
                         ["routing.expert_load", "routing.token_routing"])

    def test_new_epoch_does_not_hide_old_conflict(self):
        changed = fixture()
        changed["members"]["value"][0]["global_rank"]["value"] = 3
        result = normalize_contexts([fixture(), changed, fixture("rejoined")])
        self.assertEqual([x["index"] for x in result["contexts"]], [2])
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual(result["diagnostics"][0]["indices"], [0, 1])

    def test_fixture_hash_manifest(self):
        manifest = json.loads((ROOT / "manifest.json").read_text())
        self.assertEqual(set(manifest), {"dp_only.json", "mixed.json", "unknown.json", "missing_mapping.json", "rejoined.json", "invalid_member.json"})
        for name, digest in manifest.items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
