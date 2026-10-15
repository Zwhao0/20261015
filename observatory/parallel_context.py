"""Versioned synthetic ParallelContext sidecar; pure, bounded validation only.

No source is contacted and no authority is authenticated. C1 is not imported or
modified. Evidence labels only model the approved semantics in synthetic tests.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re


class InvalidContext(ValueError):
    """An invalid synthetic sidecar; messages never include input values."""


_TOKEN = re.compile(r"SYN_[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_REASONS = {"NO_SOURCE", "MISSING_MAPPING", "EPOCH_UNKNOWN", "NOT_OBSERVED",
            "NOT_SUPPORTED", "CONFLICT"}
_CAPABILITIES = {
    "OWNER_MANIFEST": {"membership", "rank", "process"},
    "LAUNCHER": {"membership", "rank", "process", "gpu"},
    "SCHEDULER": {"membership"},
    "LOCAL_PROCESS": {"process"},
    "DEVICE_MONITOR": {"gpu"},
    "GROUP_MANIFEST": {"topology"},
    "EXPERT_MANIFEST": {"expert"},
    "LOG_UNVERIFIED": set(), "UNKNOWN": set(),
}
_GROUP_TYPES = {"DP", "PP", "TP", "EP", "CP", "VIRTUAL_PP", "EXPERT_TENSOR"}


def _fail(path, reason):
    raise InvalidContext(path + ": " + reason)


def _obj(value, fields, path):
    if type(value) is not dict or set(value) != set(fields.split()):
        _fail(path, "expected exact object fields")
    return value


def _array(value, path, limit=256, nonempty=False):
    if type(value) is not list or len(value) > limit or (nonempty and not value):
        _fail(path, "invalid array size or type")
    return value


def _token(value, path):
    if type(value) is not str or not _TOKEN.fullmatch(value):
        _fail(path, "expected synthetic identifier")
    return value


def _int(value, path, positive=False):
    if type(value) is not int or not (int(positive) <= value <= (1 << 63) - 1):
        _fail(path, "expected bounded integer")
    return value


def _tokens(value, path, nonempty=False):
    values = _array(value, path, nonempty=nonempty)
    for item in values:
        _token(item, path)
    if len(set(values)) != len(values):
        _fail(path, "duplicate identifier")
    return values


def _scope(value, path):
    _obj(value, "job_id run_id attempt_id", path)
    for key in value:
        _token(value[key], path + "." + key)
    return value


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(value):
    return hashlib.sha256(_canonical(value).encode("ascii")).hexdigest()


def _facts(value):
    """Remove provenance, preserving values, unknowns and semantically ordered lists."""
    if type(value) is dict:
        if set(value) == {"value", "evidence", "unknown_reason"}:
            return _facts(value["value"])
        return {k: _facts(v) for k, v in value.items() if k != "evidence"}
    if type(value) is list:
        return [_facts(v) for v in value]
    return value


def _unknowns(value, path=""):
    result = []
    if type(value) is dict:
        if set(value) == {"value", "evidence", "unknown_reason"}:
            if value["value"] is None:
                result.append(path)
            else:
                result.extend(_unknowns(value["value"], path + ".value"))
        else:
            for key, item in value.items():
                result.extend(_unknowns(item, path + "." + key if path else key))
    elif type(value) is list:
        for index, item in enumerate(value):
            result.extend(_unknowns(item, path + "[" + str(index) + "]"))
    return sorted(result)


def validate_context(value):
    """Return an independent validated sidecar, or raise InvalidContext.

    Only plain dict/list/scalar objects in the documented fixed structure are
    accepted. Exact fields and bounded arrays also bound traversal depth/size.
    """
    _obj(value, "context_version origin scope membership_epoch topology_epoch members "
         "groups experts routing evidence", "context")
    if value["context_version"] != "0.1" or value["origin"] != "SYNTHETIC":
        _fail("context", "unsupported version or origin")
    scope = _scope(value["scope"], "scope")
    evidence = {}
    source_slots = set()
    for item in _array(value["evidence"], "evidence", limit=64):
        _obj(item, "evidence_id source_id source_epoch source_seq kind scope evidence_ref "
             "content_sha256 clock_domain_id observed_tick", "evidence[]")
        for key in ("evidence_id", "source_id", "source_epoch", "evidence_ref", "clock_domain_id"):
            _token(item[key], "evidence[]." + key)
        for key in ("source_seq", "observed_tick"):
            _int(item[key], "evidence[]." + key)
        if type(item["kind"]) is not str or item["kind"] not in _CAPABILITIES:
            _fail("evidence[].kind", "unsupported source kind")
        if type(item["content_sha256"]) is not str or not _SHA.fullmatch(item["content_sha256"]):
            _fail("evidence[].content_sha256", "invalid digest")
        if _scope(item["scope"], "evidence[].scope") != scope:
            _fail("evidence[].scope", "scope mismatch")
        slot = (item["source_id"], item["source_epoch"], item["source_seq"])
        if item["evidence_id"] in evidence or slot in source_slots:
            _fail("evidence", "duplicate evidence identity or source slot")
        source_slots.add(slot)
        evidence[item["evidence_id"]] = item

    def refs(items, capability, path):
        for ref in _tokens(items, path, nonempty=True):
            if ref not in evidence or capability not in _CAPABILITIES[evidence[ref]["kind"]]:
                _fail(path, "missing or unsuitable evidence")

    def claim(item, capability, path, validator):
        _obj(item, "value evidence unknown_reason", path)
        if item["value"] is None:
            if item["evidence"] != [] or type(item["evidence"]) is not list:
                _fail(path, "unknown claim must have no evidence")
            if type(item["unknown_reason"]) is not str or item["unknown_reason"] not in _REASONS:
                _fail(path, "unknown claim requires reason")
        else:
            if item["unknown_reason"] is not None:
                _fail(path, "known claim cannot have unknown reason")
            refs(item["evidence"], capability, path + ".evidence")
            validator(item["value"], path + ".value")
        return item["value"]

    me = claim(value["membership_epoch"], "membership", "membership_epoch", _int)
    te = claim(value["topology_epoch"], "topology", "topology_epoch", _int)
    worker_ids, ranks, processes, local_ranks = set(), set(), set(), set()

    def process(item, path):
        _obj(item, "host_id boot_id pid_namespace_id pid process_start_ticks start_ticks_hz", path)
        for key in ("host_id", "boot_id", "pid_namespace_id"):
            _token(item[key], path + "." + key)
        for key in ("pid", "process_start_ticks", "start_ticks_hz"):
            _int(item[key], path + "." + key, positive=key != "process_start_ticks")
        # Tick frequency is a representation property, not a different instance.
        instance = tuple(item[k] for k in ("host_id", "boot_id", "pid_namespace_id", "pid", "process_start_ticks"))
        if instance in processes:
            _fail(path, "process instance assigned to multiple workers")
        processes.add(instance)

    def members(items, path):
        if me is None:
            _fail(path, "membership epoch required")
        for item in _array(items, path, nonempty=True):
            _obj(item, "worker_id process global_rank local_rank gpu_ids", "members[]")
            wid = _token(item["worker_id"], "members[].worker_id")
            if wid in worker_ids:
                _fail("members", "duplicate worker")
            worker_ids.add(wid)
            p = claim(item["process"], "process", "members[].process", process)
            rank = claim(item["global_rank"], "rank", "members[].global_rank", _int)
            local = claim(item["local_rank"], "rank", "members[].local_rank", _int)
            claim(item["gpu_ids"], "gpu", "members[].gpu_ids", _tokens)
            if rank is not None:
                if rank in ranks:
                    _fail("members", "duplicate global rank")
                ranks.add(rank)
            if p is not None and local is not None:
                local_key = (p["host_id"], p["boot_id"], p["pid_namespace_id"], local)
                if local_key in local_ranks:
                    _fail("members", "duplicate local rank in same process domain")
                local_ranks.add(local_key)

    member_value = claim(value["members"], "membership", "members", members)
    group_map = {}

    def subset(items, allowed, path):
        _tokens(items, path, nonempty=True)
        if not set(items) <= allowed:
            _fail(path, "unmapped member reference")

    def groups(items, path):
        if me is None or te is None or member_value is None:
            _fail(path, "known epochs and members required")
        for item in _array(items, path):
            _obj(item, "group_id group_type member_ids membership_epoch topology_epoch evidence", "groups[]")
            gid = _token(item["group_id"], "groups[].group_id")
            if gid in group_map:
                _fail("groups", "duplicate group id")
            if type(item["group_type"]) is not str or item["group_type"] not in _GROUP_TYPES:
                _fail("groups[].group_type", "unsupported group type")
            for key, expected in (("membership_epoch", me), ("topology_epoch", te)):
                if _int(item[key], "groups[]." + key) != expected:
                    _fail("groups[]", "epoch mismatch")
            refs(item["evidence"], "topology", "groups[].evidence")
            subset(item["member_ids"], worker_ids, "groups[].member_ids")
            group_map[gid] = item

    claim(value["groups"], "topology", "groups", groups)
    expert_keys = set()

    def experts(items, path):
        if me is None or te is None or member_value is None:
            _fail(path, "known epochs and members required")
        for item in _array(items, path):
            _obj(item, "layer_id expert_id replica_id owner_worker_ids communication_group_ids evidence", "experts[]")
            key = tuple(_token(item[k], "experts[]." + k) for k in ("layer_id", "expert_id", "replica_id"))
            if key in expert_keys:
                _fail("experts", "duplicate expert replica")
            expert_keys.add(key)
            subset(item["owner_worker_ids"], worker_ids, "experts[].owner_worker_ids")
            refs(item["evidence"], "expert", "experts[].evidence")

            def communication(items, path):
                _tokens(items, path, nonempty=True)
                covered = set()
                for gid in items:
                    if gid not in group_map or group_map[gid]["group_type"] not in {"EP", "EXPERT_TENSOR"}:
                        _fail(path, "unmapped expert communication group")
                    covered.update(group_map[gid]["member_ids"])
                if not set(item["owner_worker_ids"]) <= covered:
                    _fail(path, "expert owner outside communication groups")

            claim(item["communication_group_ids"], "expert", "experts[].communication_group_ids", communication)

    claim(value["experts"], "expert", "experts", experts)
    _obj(value["routing"], "token_routing expert_load", "routing")
    for key in ("token_routing", "expert_load"):
        def unsupported(item, path):
            _fail(path, "dynamic observation unsupported in C2-A")
        claim(value["routing"][key], "routing", "routing." + key, unsupported)
    return copy.deepcopy(value)


def normalize_contexts(values):
    """Validate at most 128 sidecars, isolate all conflicting epoch/source slots.

    Returns no winner for a conflict. All versions remain reviewable by index
    and digest in diagnostics, never by echoing invalid input.
    """
    _array(values, "batch", limit=128)
    records, diagnostics, seen, duplicates = [], [], set(), 0
    for index, value in enumerate(values):
        try:
            context = validate_context(value)
        except InvalidContext as error:
            diagnostics.append({"code": "INVALID_CONTEXT", "indices": [index], "reason": str(error)})
            continue
        digest = _digest(context)
        if digest in seen:
            duplicates += 1
            continue
        seen.add(digest)
        records.append((index, context, digest))

    slots = {}
    for index, context, digest in records:
        scope = tuple(context["scope"][k] for k in ("job_id", "run_id", "attempt_id"))
        me, te = context["membership_epoch"]["value"], context["topology_epoch"]["value"]
        checks = []
        if me is not None:
            checks.append((("MEMBERSHIP_CONFLICT", scope, me), _facts(context["members"])))
        if te is not None:
            checks.append((("TOPOLOGY_CONFLICT", scope, te), [me, _facts(context["groups"]), _facts(context["experts"])]))
        for item in context["evidence"]:
            # Source namespace includes scope; never join unrelated attempts.
            key = ("SOURCE_CONFLICT", scope, item["source_id"], item["source_epoch"], item["source_seq"])
            fact = {k: v for k, v in item.items() if k != "evidence_id"}
            checks.append((key, fact))
        for key, fact in checks:
            slots.setdefault(key, []).append((index, _digest(fact), digest))

    quarantined = set()
    for key, entries in slots.items():
        if len({fact for _, fact, _ in entries}) > 1:
            indices = sorted({index for index, _, _ in entries})
            quarantined.update(indices)
            diagnostics.append({"code": key[0], "indices": indices,
                                "digests": sorted({digest for _, _, digest in entries})})
    accepted = []
    for index, context, digest in records:
        if index in quarantined:
            continue
        unknown_paths = _unknowns(context)
        status = "UNKNOWN" if any(not p.startswith("routing.") for p in unknown_paths) else "SYNTHETIC_SUPPORTED"
        accepted.append({"index": index, "digest": digest, "context": context,
                         "status": status, "unknown_paths": unknown_paths})
    status = "UNKNOWN" if not accepted or diagnostics or any(x["status"] == "UNKNOWN" for x in accepted) else "SYNTHETIC_SUPPORTED"
    return {"contexts": accepted, "diagnostics": diagnostics, "duplicates": duplicates, "status": status}
