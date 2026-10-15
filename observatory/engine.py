"""Evidence aggregation; source order never implies cross-source causality."""

import copy
import hashlib
import json

from .contract import InvalidRecord, validate_record


MAX_LINE_BYTES = 16 * 1024
MAX_RECORDS = 1000
IDENTITY_FIELDS = (
    "job_id", "run_id", "attempt_id", "scope", "host_id", "boot_id",
    "pid_namespace_id", "pid", "process_start_ticks", "start_ticks_hz",
    "rank", "local_rank", "world_size", "gpu_uuids",
)
INSTANCE_FIELDS = ("host_id", "boot_id", "pid_namespace_id", "pid", "process_start_ticks")
TRUSTED = {"parent_wait", "launcher", "scheduler"}
BAD_COVERAGE = {"UNKNOWN", "GAP", "STALE", "UNAVAILABLE", "INVALID_RECORD", "CONFLICT"}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def event_key(record):
    return record["source_id"], record["source_epoch"], record["source_seq"]


def run_key(identity):
    if identity["job_id"] is not None and identity["run_id"] is not None:
        return identity["job_id"], identity["run_id"]
    return None


def attempt_key(identity):
    key = run_key(identity)
    return key + (identity["attempt_id"],) if key and identity["attempt_id"] is not None else None


def process_key(identity):
    key = attempt_key(identity)
    required = INSTANCE_FIELDS + ("start_ticks_hz",)
    if identity["scope"] == "worker":
        required += ("rank", "local_rank", "world_size", "gpu_uuids")
    if key and identity["scope"] in {"worker", "launcher"} and all(identity[f] is not None for f in required):
        return key + (identity["scope"],) + tuple(identity[f] for f in INSTANCE_FIELDS)
    return None


def age_ms(event_ns, event_domain, observed_ns, observed_domain):
    if (event_ns is None or observed_ns is None or event_domain is None
            or event_domain != observed_domain or observed_ns < event_ns):
        return None
    delta = observed_ns - event_ns
    # Avoid float overflow and imprecise timing claims for adversarial integers.
    if delta > (2 ** 53 - 1) * 1_000_000:
        return None
    return delta / 1_000_000


def lifecycle(payload):
    if payload["authority"] not in TRUSTED:
        return "UNKNOWN"
    if payload["status_kind"] == "EXITED":
        return "EXITED_OK" if payload["exit_code"] == 0 else "EXITED_NONZERO"
    if payload["status_kind"] == "SIGNALED":
        return "EXITED_SIGNAL"
    return "UNKNOWN"


class Replay:
    """Bounded finite replay. No real clock, file dereferencing, or external I/O."""

    def __init__(self, max_records=MAX_RECORDS):
        if type(max_records) is not int or not 1 <= max_records <= MAX_RECORDS:
            raise ValueError("max_records must be 1..1000")
        self.max_records = max_records
        self.slots = {}
        self.events = []
        self.diagnostics = []
        self.invalid_sources = set()
        self.arrivals = 0
        self.duplicates = 0
        self.limit_reported = False
        self.unscoped_invalid = False

    def reject(self, code, source=None):
        self.diagnostics.append({"arrival_index": self.arrivals, "code": code})
        if source:
            self.invalid_sources.add(source)
        elif code != "CONFLICT":
            self.unscoped_invalid = True

    def feed(self, raw):
        self.arrivals += 1
        if self.arrivals > self.max_records:
            if not self.limit_reported:
                self.reject("QUEUE_LIMIT")
                self.limit_reported = True
            return
        if len(raw) > MAX_LINE_BYTES:
            self.reject("LINE_LIMIT")
            return
        if not raw.endswith(b"\n"):
            self.reject("INCOMPLETE_FRAME")
            return
        record = None
        try:
            def pairs(items):
                result = {}
                for key, value in items:
                    if key in result:
                        raise ValueError("duplicate JSON key")
                    result[key] = value
                return result
            record = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                                parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
            normalized = validate_record(record)
            fingerprint = digest(record)
        except (InvalidRecord, ValueError, TypeError, UnicodeError, RecursionError, OverflowError):
            source = record.get("source_id") if isinstance(record, dict) else None
            known = {key[0] for key in self.slots}
            self.reject("INVALID_RECORD", source if isinstance(source, str) and source in known else None)
            return
        key = event_key(normalized)
        if key in self.slots:
            slot = self.slots[key]
            if fingerprint in slot["fingerprints"]:
                self.duplicates += 1
            else:
                slot["fingerprints"].add(fingerprint)
                slot["variants"].append(normalized)
                self.reject("CONFLICT")
            return
        normalized["event_id"] = "evt_" + digest(list(key))
        self.slots[key] = {"fingerprints": {fingerprint}, "variants": [normalized]}
        self.events.append({"type": "NORMALIZED_EVENT", "arrival_index": self.arrivals, "record": normalized})

    def result(self):
        records = [slot["variants"][0] for key, slot in sorted(self.slots.items())
                   if len(slot["variants"]) == 1]
        conflicted = [r for slot in self.slots.values() if len(slot["variants"]) > 1 for r in slot["variants"]]
        sources = self._sources(records, conflicted)
        coverage = {(s["source_id"], s["source_epoch"]): s["coverage_status"] for s in sources}
        processes, attempts, runs, exits = self._aggregate(records, conflicted, coverage)
        if self.limit_reported:
            for row in attempts + runs:
                row["lifecycle"] = "UNKNOWN"
                row["terminal_evidence_ref"] = None
                if "terminal_evidence_refs" in row:
                    row["terminal_evidence_refs"] = []
                row["coverage_status"] = "UNKNOWN"
        events = []
        for event in self.events:
            key = event_key(event["record"])
            slot = self.slots[key]
            if len(slot["variants"]) > 1:
                events.append({"type": "CONFLICT_EVENT", "arrival_index": event["arrival_index"],
                               "source_key": list(key), "variant_hashes": sorted(slot["fingerprints"])})
            else:
                events.append(copy.deepcopy(event))
        return {
            "schema_version": "0.1", "input_integrity": "UNKNOWN" if self.diagnostics else "COMPLETE",
            "events": events,
            "diagnostics": copy.deepcopy(self.diagnostics), "sources": sources,
            "processes": processes, "attempts": attempts, "runs": runs, "exits": exits,
            "counts": {"arrivals": self.arrivals, "accepted": len(self.slots),
                       "duplicates": self.duplicates, "invalid": len(self.diagnostics)},
        }

    def _sources(self, records, conflicts):
        groups = {}
        for record in records + conflicts:
            groups.setdefault(event_key(record)[:2], []).append(record)
        output = []
        for key, group in sorted(groups.items()):
            seqs = sorted({r["source_seq"] for r in group})
            # Range expansion is forbidden for attacker-controlled sequence numbers.
            gap = any(b > a + 1 for a, b in zip(seqs, seqs[1:]))
            status_records = sorted((r for r in group if r["event_type"] == "SOURCE_STATUS"),
                                    key=lambda r: r["source_seq"])
            status = "UNKNOWN"
            mode, read = "UNKNOWN", "UNKNOWN"
            record_age, read_time = None, None
            historical = ["GAP"] if gap else []
            for record in status_records:
                p = record["payload"]
                if p["status"] in BAD_COVERAGE:
                    historical.append(p["status"])
            if status_records:
                record = status_records[-1]
                p, t = record["payload"], record["time"]
                mode, read, status = p["source_mode"], p["read_status"], p["status"]
                read_time = p["last_successful_read_monotonic_ns"]
                # Record age was measured at the last successful read in this same domain.
                delta = age_ms(read_time, t["observed_clock_domain_id"],
                               t["observed_monotonic_ns"], t["observed_clock_domain_id"])
                record_age = p["last_record_age_ms"]
                if record_age is not None and record_age <= 2 ** 53 - 1 and delta is not None:
                    record_age += delta
                else:
                    record_age = None
                if read != "OK":
                    status = "UNAVAILABLE" if read == "UNAVAILABLE" else "UNKNOWN"
                elif mode == "UNKNOWN":
                    status = "UNKNOWN"
                elif mode == "PERIODIC" and status in {"OK", "STALE"}:
                    if record_age is None:
                        status = "UNKNOWN"
                    elif record_age > p["freshness_timeout_ms"]:
                        status = "STALE"
                    elif status == "STALE":
                        status = "UNKNOWN"
            contracts = {(r["payload"]["source_mode"], r["payload"]["expected_interval_ms"],
                          r["payload"]["freshness_timeout_ms"]) for r in status_records}
            conflict = len(contracts) > 1 or any(event_key(r)[:2] == key for r in conflicts)
            if conflict:
                status = "CONFLICT"
                historical.append("CONFLICT")
            if key[0] in self.invalid_sources:
                historical.append("INVALID_RECORD")
            if gap:
                status = "GAP" if not conflict else "CONFLICT"
            if self.unscoped_invalid and status not in BAD_COVERAGE:
                status = "UNKNOWN"
            degraded = self.unscoped_invalid or bool(historical) or status in BAD_COVERAGE
            output.append({"source_id": key[0], "source_epoch": key[1], "source_mode": mode,
                           "status": status, "read_status": read, "producer_liveness": "UNKNOWN",
                           "last_record_age_ms": record_age,
                           "last_successful_read_monotonic_ns": read_time,
                           "coverage_status": "UNKNOWN" if degraded else "COMPLETE",
                           "history": sorted(set(historical)), "sequence_gap": gap})
        return output

    def _aggregate(self, records, conflicts, coverage):
        procs, ats, rs = {}, {}, {}
        manifests, proofs = {}, {}
        conflict_p, conflict_a, conflict_r = set(), set(), set()
        for record in conflicts:
            ident = record["identity"]
            pk, ak, rk = process_key(ident), attempt_key(ident), run_key(ident)
            if pk:
                conflict_p.add(pk)
            if ak:
                conflict_a.add(ak)
            if rk:
                conflict_r.add(rk)
        for record in conflicts:
            ident = record["identity"]
            rk, ak = run_key(ident), attempt_key(ident)
            if rk:
                rs.setdefault(rk, {"evidence": set(), "coverage": ["UNKNOWN"]})
            if ak:
                ats.setdefault(ak, {"evidence": set(), "coverage": ["UNKNOWN"]})
            pk = process_key(ident)
            if pk:
                procs.setdefault(pk, {"identity": ident, "evidence": set(), "coverage": ["UNKNOWN"],
                                      "facts": {}, "snapshots": []})
        for record in records:
            ident, p = record["identity"], record["payload"]
            pk, ak, rk = process_key(ident), attempt_key(ident), run_key(ident)
            source_coverage = coverage[event_key(record)[:2]]
            if rk:
                rs.setdefault(rk, {"evidence": set(), "coverage": []})
                rs[rk]["evidence"].add(record["evidence_ref"])
                rs[rk]["coverage"].append(source_coverage)
            if ak:
                ats.setdefault(ak, {"evidence": set(), "coverage": []})
                ats[ak]["evidence"].add(record["evidence_ref"])
                ats[ak]["coverage"].append(source_coverage)
            if record["event_type"] == "IDENTITY" and ak:
                manifests.setdefault(ak, []).append(record)
            if record["event_type"] == "RUN_TERMINAL" and rk:
                proofs.setdefault(rk, []).append(record)
            if not pk:
                continue
            proc = procs.setdefault(pk, {"identity": ident, "evidence": set(), "coverage": [],
                                         "facts": {}, "snapshots": []})
            # A single instance cannot silently acquire contradictory rank/GPU bindings.
            if any(proc["identity"][f] != ident[f] for f in IDENTITY_FIELDS):
                conflict_p.add(pk)
            proc["evidence"].add(record["evidence_ref"])
            proc["coverage"].append(source_coverage)
            if record["event_type"] == "PROCESS_EXIT" and lifecycle(p) != "UNKNOWN" and p["scope"] == ident["scope"]:
                fact = (p["status_kind"], p["exit_code"], p["signal"])
                proc["facts"].setdefault(fact, []).append(record)
            if record["event_type"] == "SNAPSHOT":
                proc["snapshots"].append(record)
        process_output, exits = [], []
        for pk, proc in sorted(procs.items()):
            facts = proc["facts"]
            bad = pk in conflict_p or len(facts) > 1
            state = "UNKNOWN"
            refs = []
            expected = None
            if len(facts) == 1 and not bad:
                fact_records = next(iter(facts.values()))
                state = lifecycle(fact_records[0]["payload"])
                refs = sorted({r["evidence_ref"] for r in fact_records})
                stops = {r["payload"]["expected_stop"] for r in fact_records}
                expected = next(iter(stops)) if len(stops) == 1 else None
                exits.append({"process_key": list(pk), "lifecycle": state, "evidence_refs": refs,
                              "expected_stop": expected, "root_cause": "UNKNOWN"})
            if bad:
                conflict_a.add(pk[:3])
                conflict_r.add(pk[:2])
            snapshots = proc["snapshots"]
            # Cross-source samples have no defensible total chronological order.
            latest = None
            if len({event_key(r)[:2] for r in snapshots}) == 1:
                latest = max(snapshots, key=lambda r: r["source_seq"], default=None)
            age = None
            presence, progress, metrics = "UNKNOWN", None, []
            if latest:
                t = latest["time"]
                age = age_ms(t["event_monotonic_ns"], t["event_clock_domain_id"],
                             t["observed_monotonic_ns"], t["observed_clock_domain_id"])
                if coverage[event_key(latest)[:2]] == "COMPLETE" and not bad:
                    presence = latest["payload"]["process_presence"]
                    progress = latest["payload"]["progress"]
                    metrics = latest["payload"]["device_samples"]
            proc["lifecycle"] = state
            process_output.append({"key": list(pk), "identity": proc["identity"],
                                   "identity_status": "UNKNOWN" if bad else "COMPLETE",
                                   "coverage_status": "UNKNOWN" if bad or "UNKNOWN" in proc["coverage"] else "COMPLETE",
                                   "lifecycle": state, "evidence_refs": sorted(proc["evidence"]),
                                   "last_observed_age_ms": age, "process_presence": presence,
                                   "progress": progress, "device_samples": metrics,
                                   "terminal_evidence_refs": refs})
        attempt_output = []
        for ak, data in sorted(ats.items()):
            ms = manifests.get(ak, [])
            complete = [m for m in ms if m["payload"]["membership_complete"]]
            member_sets = []
            member_bindings = []
            invalid_manifest = False
            for m in complete:
                members = m["payload"]["members"]
                keys = [process_key(i) for i in members]
                ranks = [i["rank"] for i in members]
                world = m["identity"]["world_size"]
                valid = (type(world) is int and len(keys) == world and all(keys)
                         and len(set(keys)) == world and set(ranks) == set(range(world))
                         and all(k[:3] == ak and k[3] == "worker" for k in keys)
                         and all(i["world_size"] == world for i in members))
                if valid:
                    for member, key in zip(members, keys):
                        if key in procs and any(member[f] != procs[key]["identity"][f] for f in IDENTITY_FIELDS):
                            valid = False
                if valid:
                    member_sets.append(frozenset(keys))
                    member_bindings.append(digest(sorted(members, key=process_key)))
                else:
                    invalid_manifest = True
            expected = next(iter(member_sets), frozenset())
            consistent = (bool(member_sets) and not invalid_manifest and len(set(member_bindings)) == 1
                          and all(s == expected for s in member_sets))
            known = {pk for pk in procs if pk[:3] == ak and pk[3] == "worker"}
            # Unlisted workers are a membership contradiction, never silently ignored.
            if expected and not known.issubset(expected):
                consistent = False
            terminated = {pk for pk in expected if pk in procs and procs[pk]["lifecycle"] != "UNKNOWN"}
            failures = sorted([list(pk) for pk in known if procs[pk]["lifecycle"] in {"EXITED_NONZERO", "EXITED_SIGNAL"}])
            state = "UNKNOWN"
            bad = ak in conflict_a
            if consistent and not bad and terminated == expected:
                state = "ATTEMPT_EXITED_WITH_FAILURE" if failures else "ATTEMPT_EXITED_OK"
            data["lifecycle"] = state
            terminal_refs = sorted({r["evidence_ref"] for pk in terminated
                                    for records_for_fact in procs[pk]["facts"].values()
                                    for r in records_for_fact}) if state != "UNKNOWN" else []
            attempt_output.append({"key": list(ak), "identity_status": "COMPLETE" if consistent and not bad else "UNKNOWN",
                                   "coverage_status": "UNKNOWN" if bad or "UNKNOWN" in data["coverage"] else "COMPLETE",
                                   "lifecycle": state, "expected_members": len(expected) if consistent else None,
                                   "known_members": len(known), "terminated_members": len(terminated),
                                   "failure_facts": failures, "evidence_refs": sorted(data["evidence"]),
                                   "terminal_evidence_ref": (terminal_refs[0] if len(terminal_refs) == 1
                                                             else "derived_" + digest(terminal_refs)) if terminal_refs else None,
                                   "terminal_evidence_refs": terminal_refs})
        run_output = []
        for rk, data in sorted(rs.items()):
            candidates = []
            for record in proofs.get(rk, []):
                p = record["payload"]
                if p["authority"] not in {"scheduler", "launcher"} or p["outcome"] is None:
                    continue
                if p["proof_kind"] == "RUN_TERMINAL":
                    candidates.append((p["outcome"], None, record["evidence_ref"]))
                elif p["no_restart_or_resume"] is True and p["final_attempt_id"] is not None:
                    ak = rk + (p["final_attempt_id"],)
                    state = ats.get(ak, {}).get("lifecycle", "UNKNOWN")
                    if p["outcome"] != "COMPLETED" or state == "ATTEMPT_EXITED_OK":
                        candidates.append((p["outcome"], p["final_attempt_id"], record["evidence_ref"]))
            conclusions = {(c[0], c[1]) for c in candidates}
            bad = rk in conflict_r or len({c[0] for c in candidates}) > 1 or len({c[1] for c in candidates if c[1]}) > 1
            state, final, ref = "UNKNOWN", None, None
            final_candidates = {c[1] for c in candidates if c[1]}
            if final_candidates:
                # A new attempt contradicts a no-restart proof unless explicitly the final one.
                final_proof_records = [r for r in proofs.get(rk, []) if r["payload"]["proof_kind"] == "FINAL_ATTEMPT"]
                for proof_record in final_proof_records:
                    for r in records:
                        other = attempt_key(r["identity"])
                        if (other and other[:2] == rk and other[2] not in final_candidates
                                and r["source_id"] == proof_record["source_id"]
                                and r["source_epoch"] == proof_record["source_epoch"]
                                and r["source_seq"] > proof_record["source_seq"]):
                            bad = True
            if conclusions and not bad:
                state = candidates[0][0]
                final_ids = {c[1] for c in candidates if c[1]}
                final = next(iter(final_ids)) if final_ids else None
                ref = sorted(c[2] for c in candidates)[0]
            children = [a for a in attempt_output if tuple(a["key"][:2]) == rk]
            run_output.append({"key": list(rk), "identity_status": "UNKNOWN" if bad else "COMPLETE",
                               "coverage_status": "UNKNOWN" if bad or "UNKNOWN" in data["coverage"] else "COMPLETE",
                               "lifecycle": state, "final_attempt_id": final, "terminal_evidence_ref": ref,
                               "expected_members": sum(a["expected_members"] for a in children)
                               if children and all(a["expected_members"] is not None for a in children) else None,
                               "known_members": sum(a["known_members"] for a in children),
                               "terminated_members": sum(a["terminated_members"] for a in children),
                               "failure_facts": [f for a in children for f in a["failure_facts"]],
                               "evidence_refs": sorted(data["evidence"])})
        return process_output, attempt_output, run_output, exits


def replay(lines, max_records=MAX_RECORDS):
    engine = Replay(max_records)
    for line in lines:
        engine.feed(line)
        if engine.limit_reported:
            break
    return engine.result()
