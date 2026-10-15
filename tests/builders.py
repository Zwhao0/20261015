"""Synthetic public inputs; these do not access processes or devices."""

import copy
import json


def identity(**changes):
    value = dict(job_id="SYN_JOB", run_id="SYN_RUN", attempt_id="SYN_ATTEMPT_0",
                 world_size=1, rank=0, local_rank=0, scope="worker", host_id="SYN_HOST_A",
                 boot_id="SYN_BOOT_A", pid_namespace_id="SYN_NS_A", pid=100,
                 process_start_ticks=10, start_ticks_hz=100, gpu_uuids=["SYN_GPU_A"])
    value.update(changes)
    return value


def event(kind="SNAPSHOT", seq=0, ident=None, payload=None, source="SYN_SOURCE_A", epoch="SYN_EPOCH_0", **changes):
    ident = copy.deepcopy(ident or identity())
    if payload is None:
        payload = dict(process_presence="OBSERVED", device_samples=[], progress=None)
    value = dict(schema_version="0.1", event_id="SYN_EVENT_" + str(seq), event_type=kind,
                 source_id=source, source_epoch=epoch, source_seq=seq, origin="SYNTHETIC",
                 identity=ident, time=dict(event_time_utc="2026-10-15T00:00:00Z",
                                          observed_time_utc="2026-10-15T00:00:00Z",
                                          event_monotonic_ns=0, observed_monotonic_ns=0,
                                          event_clock_domain_id="SYN_CLOCK_A", observed_clock_domain_id="SYN_CLOCK_A",
                                          uncertainty_ms=0), payload=copy.deepcopy(payload),
                 evidence_ref="SYN_EVIDENCE_" + source + "_" + str(seq),
                 source_cursor="SYN_CURSOR_" + str(seq), content_sha256="a" * 64,
                 unknown_reasons={})
    def nulls(obj, path):
        if isinstance(obj, dict):
            for key, val in obj.items():
                nulls(val, path + "." + key if path else key)
        elif isinstance(obj, list):
            for index, val in enumerate(obj):
                nulls(val, path + "[" + str(index) + "]")
        elif obj is None:
            value["unknown_reasons"][path] = "not_supplied"
    nulls(ident, "identity")
    nulls(payload, "payload")
    value.update(changes)
    return value


def manifest(seq=0, members=None, ident=None, complete=True):
    ident = ident or identity()
    return event("IDENTITY", seq, identity(**{**ident, "scope": "attempt"}),
                 dict(scope="attempt", members=members or [ident], membership_complete=complete))


def exited(seq=1, ident=None, code=0, source="SYN_SOURCE_A", authority="parent_wait", **changes):
    ident = ident or identity()
    p = dict(scope=ident["scope"], authority=authority, status_kind="EXITED", raw_status=code * 256,
             raw_status_format="posix_wait", exit_code=code, signal=None, expected_stop=False)
    p.update(changes)
    return event("PROCESS_EXIT", seq, ident, p, source)


def terminal(seq=2, proof="RUN_TERMINAL", outcome="COMPLETED", final=None, no_restart=None, source="SYN_SOURCE_A"):
    return event("RUN_TERMINAL", seq, identity(scope="run", attempt_id=None),
                 dict(scope="run", authority="scheduler", proof_kind=proof, outcome=outcome,
                      final_attempt_id=final, no_restart_or_resume=no_restart), source)


def status(seq=0, mode="EVENT_DRIVEN", state="IDLE", read="OK", age=0, now=0, source="SYN_SOURCE_A"):
    p = dict(source_mode=mode, expected_interval_ms=5000 if mode == "PERIODIC" else None,
             freshness_timeout_ms=15000 if mode == "PERIODIC" else None,
             last_successful_read_monotonic_ns=now, last_record_age_ms=age,
             status=state, read_status=read, reason="synthetic", affected_source_id=source)
    e = event("SOURCE_STATUS", seq, identity(scope="run", attempt_id=None, pid=None, rank=None), p, source)
    e["time"]["event_monotonic_ns"] = now
    e["time"]["observed_monotonic_ns"] = now
    return e


def line(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
