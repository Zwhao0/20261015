"""Strict validator and normalizer for synthetic schema 0.1 records.

This module is deliberately limited to the offline public record contract. It
does not read evidence references, contact a source, or infer task state.
"""

from __future__ import annotations

import copy
import datetime as _datetime
import math
import os
import re
from typing import Any


class InvalidRecord(ValueError):
    """Raised when a record is outside the public schema 0.1 contract."""


_TOP_LEVEL = (
    "schema_version",
    "event_id",
    "event_type",
    "source_id",
    "source_epoch",
    "source_seq",
    "origin",
    "identity",
    "time",
    "payload",
    "evidence_ref",
    "unknown_reasons",
    "source_cursor",
    "content_sha256",
)
_IDENTITY_FIELDS = (
    "scope",
    "job_id",
    "run_id",
    "attempt_id",
    "world_size",
    "rank",
    "local_rank",
    "host_id",
    "boot_id",
    "pid_namespace_id",
    "pid",
    "process_start_ticks",
    "start_ticks_hz",
    "gpu_uuids",
)
_TIME_FIELDS = (
    "event_time_utc",
    "observed_time_utc",
    "event_monotonic_ns",
    "observed_monotonic_ns",
    "event_clock_domain_id",
    "observed_clock_domain_id",
    "uncertainty_ms",
)
_EVENT_TYPES = ("IDENTITY", "SNAPSHOT", "PROCESS_EXIT", "RUN_TERMINAL", "SOURCE_STATUS")
_SCOPES = ("worker", "launcher", "attempt", "run")
_EVENT_TIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$"
)
_SYNTHETIC_TOKEN_RE = re.compile(r"^SYN_[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SENTINEL_METRICS = frozenset((-1, (1 << 32) - 1, (1 << 64) - 1))
_SECRET_TEXT_RE = re.compile(
    r"(?i)(?:\bbearer\s+|\b(?:api[_-]?key|access[_-]?token|password|secret|token)\s*[:=]\s*\S+|\bsk-[a-z0-9_-]{12,})"
)


def _fail(path: str, reason: str) -> None:
    """Raise a stable error containing schema paths only, never input values."""

    raise InvalidRecord(f"{path}: {reason}")


def _object(value: Any, fields: tuple[str, ...], path: str) -> dict[str, Any]:
    if type(value) is not dict:
        _fail(path, "expected object")
    if any(type(key) is not str for key in value):
        _fail(path, "object keys must be strings")
    if any(key not in fields for key in value):
        _fail(path, "unexpected field")
    for field in fields:
        if field not in value:
            _fail(f"{path}.{field}" if path else field, "missing required field")
    return value


def _enum(value: Any, choices: tuple[str, ...], path: str) -> str:
    if type(value) is not str or value not in choices:
        _fail(path, "invalid enum value")
    return value


def _safe_text(value: Any, path: str, *, allow_empty: bool = False) -> str:
    if type(value) is not str or (not allow_empty and not value.strip()):
        _fail(path, "expected non-empty text")
    # Free-text evidence/reasons must not smuggle paths or common credentials
    # into a synthetic export. Do not echo rejected text in the exception.
    if len(value) > 256 or "/" in value or "\\" in value or "@" in value:
        _fail(path, "unsafe text")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        _fail(path, "unsafe text")
    if _SECRET_TEXT_RE.search(value):
        _fail(path, "unsafe text")
    return value


def _token(value: Any, path: str) -> str:
    if (type(value) is not str or _SYNTHETIC_TOKEN_RE.fullmatch(value) is None
            or _SECRET_TEXT_RE.search(value)):
        _fail(path, "expected SYN_ synthetic token")
    return value


def _integer(value: Any, path: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        _fail(path, "expected integer in range")
    return value


def _number(value: Any, path: str, *, minimum: float | None = None) -> int | float:
    if type(value) not in (int, float):
        _fail(path, "expected finite number")
    if type(value) is float and not math.isfinite(value):
        _fail(path, "expected finite number")
    if minimum is not None and value < minimum:
        _fail(path, "number out of range")
    return value


class _RecordValidator:
    def __init__(self, record: dict[str, Any]):
        self.record = record
        reasons = record["unknown_reasons"]
        if type(reasons) is not dict:
            _fail("unknown_reasons", "expected object")
        if any(type(key) is not str for key in reasons):
            _fail("unknown_reasons", "reason paths must be strings")
        for reason in reasons.values():
            _safe_text(reason, "unknown_reasons")
        self.reasons: dict[str, str] = reasons
        self.known_paths: set[str] = set()
        self.null_paths: set[str] = set()

    def _field(self, path: str) -> None:
        self.known_paths.add(path)

    def _nullable(self, path: str) -> None:
        self._field(path)
        self.null_paths.add(path)

    def _reason_for(self, path: str, text: str) -> None:
        self._nullable(path)
        self.reasons.setdefault(path, text)

    def _text_or_null(self, value: Any, path: str, *, token: bool = False) -> None:
        self._field(path)
        if value is None:
            self.null_paths.add(path)
            return
        if token:
            _token(value, path)
        else:
            _safe_text(value, path)

    def _integer_or_null(
        self, value: Any, path: str, *, minimum: int = 0
    ) -> None:
        self._field(path)
        if value is None:
            self.null_paths.add(path)
        else:
            _integer(value, path, minimum=minimum)

    def validate_identity(self, identity: Any, path: str) -> None:
        identity = _object(identity, _IDENTITY_FIELDS, path)
        for field in _IDENTITY_FIELDS:
            field_path = f"{path}.{field}"
            value = identity[field]
            if field == "scope":
                self._field(field_path)
                _enum(value, _SCOPES, field_path)
            elif field in ("job_id", "run_id", "attempt_id", "host_id", "boot_id", "pid_namespace_id"):
                self._text_or_null(value, field_path, token=True)
            elif field in ("world_size", "rank", "local_rank", "pid", "process_start_ticks", "start_ticks_hz"):
                minimum = 1 if field in ("world_size", "pid", "start_ticks_hz") else 0
                self._integer_or_null(value, field_path, minimum=minimum)
            elif field == "gpu_uuids":
                self._field(field_path)
                if value is None:
                    self.null_paths.add(field_path)
                else:
                    if type(value) is not list:
                        _fail(field_path, "expected array or null")
                    for index, gpu_uuid in enumerate(value):
                        _token(gpu_uuid, f"{field_path}[{index}]")

        world_size = identity["world_size"]
        rank = identity["rank"]
        if world_size is not None and rank is not None and rank >= world_size:
            _fail(f"{path}.rank", "rank outside world size")

    def validate_time(self, time_value: Any) -> None:
        time_value = _object(time_value, _TIME_FIELDS, "time")
        for field in _TIME_FIELDS:
            path = f"time.{field}"
            value = time_value[field]
            if field in ("event_time_utc", "observed_time_utc"):
                self._field(path)
                if value is None:
                    self.null_paths.add(path)
                elif type(value) is not str:
                    _fail(path, "expected UTC text or null")
                elif not self._valid_utc(value):
                    time_value[field] = None
                    self._reason_for(path, "invalid UTC timestamp")
            elif field in ("event_monotonic_ns", "observed_monotonic_ns"):
                self._integer_or_null(value, path)
            elif field in ("event_clock_domain_id", "observed_clock_domain_id"):
                self._text_or_null(value, path, token=True)
            else:
                self._field(path)
                if value is None:
                    self.null_paths.add(path)
                else:
                    _number(value, path, minimum=0)

    @staticmethod
    def _valid_utc(value: str) -> bool:
        if _EVENT_TIME_RE.fullmatch(value) is None:
            return False
        try:
            _datetime.datetime.fromisoformat(value[:-1] + "+00:00")
        except ValueError:
            return False
        return True

    def validate_identity_payload(self, payload: Any) -> None:
        payload = _object(payload, ("scope", "members", "membership_complete"), "payload")
        self._field("payload.scope")
        scope = _enum(payload["scope"], _SCOPES, "payload.scope")
        if scope != self.record["identity"]["scope"]:
            _fail("payload.scope", "scope does not match record identity")
        members = payload["members"]
        self._field("payload.members")
        if type(members) is not list:
            _fail("payload.members", "expected array")
        for index, member in enumerate(members):
            self.validate_identity(member, f"payload.members[{index}]")
        self._field("payload.membership_complete")
        if type(payload["membership_complete"]) is not bool:
            _fail("payload.membership_complete", "expected boolean")
        if payload["membership_complete"]:
            if scope != "attempt":
                _fail("payload.membership_complete", "complete membership requires attempt scope")
            if any(member["scope"] != "worker" for member in members):
                _fail("payload.members", "complete membership requires worker members")

    def validate_snapshot_payload(self, payload: Any) -> None:
        payload = _object(
            payload, ("process_presence", "device_samples", "progress"), "payload"
        )
        self._field("payload.process_presence")
        _enum(
            payload["process_presence"],
            ("OBSERVED", "NOT_OBSERVED", "UNKNOWN"),
            "payload.process_presence",
        )
        samples = payload["device_samples"]
        self._field("payload.device_samples")
        if type(samples) is not list:
            _fail("payload.device_samples", "expected array")
        for index, sample in enumerate(samples):
            sample_path = f"payload.device_samples[{index}]"
            sample = _object(sample, ("gpu_uuid", "metrics"), sample_path)
            gpu_path = f"{sample_path}.gpu_uuid"
            self._text_or_null(sample["gpu_uuid"], gpu_path, token=True)
            metrics_path = f"{sample_path}.metrics"
            metrics = sample["metrics"]
            if type(metrics) is not dict:
                _fail(metrics_path, "expected object")
            if any(type(key) is not str for key in metrics):
                _fail(metrics_path, "object keys must be strings")
            allowed = ("memory_used", "memory_total", "utilization")
            if any(key not in allowed for key in metrics):
                _fail(metrics_path, "unexpected metric")
            for name, metric in metrics.items():
                self.validate_metric(metric, f"{metrics_path}.{name}", name)
        self.validate_progress(payload["progress"])

    def validate_metric(self, metric: Any, path: str, name: str) -> None:
        metric = _object(metric, ("value", "unit", "status"), path)
        unit_path = f"{path}.unit"
        self._field(unit_path)
        expected_unit = "percent" if name == "utilization" else "bytes"
        if metric["unit"] != expected_unit:
            _fail(unit_path, "unit does not match metric")
        status_path = f"{path}.status"
        self._field(status_path)
        status = _enum(metric["status"], ("OK", "UNKNOWN", "ERROR"), status_path)
        value_path = f"{path}.value"
        value = metric["value"]
        self._field(value_path)
        if value is not None:
            value = _number(value, value_path)
        if status != "OK" and value is not None:
            metric["value"] = None
            self._reason_for(value_path, f"metric status {status}")
        elif value is None:
            self.null_paths.add(value_path)
        elif value in _SENTINEL_METRICS:
            metric["value"] = None
            metric["status"] = "UNKNOWN"
            self.reasons.setdefault(status_path, "metric sentinel value")
            self._reason_for(value_path, "metric sentinel value")
        elif value < 0 or (name == "utilization" and value > 100):
            _fail(value_path, "metric value out of range")

    def validate_progress(self, progress: Any) -> None:
        path = "payload.progress"
        self._field(path)
        if progress is None:
            self.null_paths.add(path)
            return
        progress = _object(progress, ("step", "semantics", "source_id"), path)
        step_path = f"{path}.step"
        self._integer_or_null(progress["step"], step_path)
        semantics_path = f"{path}.semantics"
        self._text_or_null(progress["semantics"], semantics_path)
        self._text_or_null(progress["source_id"], f"{path}.source_id", token=True)

    def validate_process_exit_payload(self, payload: Any) -> None:
        fields = (
            "scope",
            "authority",
            "status_kind",
            "raw_status",
            "raw_status_format",
            "exit_code",
            "signal",
            "expected_stop",
        )
        payload = _object(payload, fields, "payload")
        self._field("payload.scope")
        scope = _enum(payload["scope"], ("worker", "launcher"), "payload.scope")
        if self.record["identity"]["scope"] != scope:
            _fail("payload.scope", "scope does not match record identity")
        self._field("payload.authority")
        _enum(
            payload["authority"],
            ("parent_wait", "launcher", "scheduler", "log_unverified", "UNKNOWN"),
            "payload.authority",
        )
        self._field("payload.status_kind")
        status = _enum(payload["status_kind"], ("EXITED", "SIGNALED", "UNKNOWN"), "payload.status_kind")
        raw_format = _enum(
            payload["raw_status_format"],
            ("posix_wait", "subprocess_returncode", "shell_unverified", "UNKNOWN"),
            "payload.raw_status_format",
        )
        self._field("payload.raw_status_format")

        raw = payload["raw_status"]
        self._field("payload.raw_status")
        if raw is None:
            self.null_paths.add("payload.raw_status")
        elif type(raw) is not int:
            _fail("payload.raw_status", "expected integer or null")

        self._field("payload.exit_code")
        exit_code = payload["exit_code"]
        if exit_code is None:
            self.null_paths.add("payload.exit_code")
        else:
            _integer(exit_code, "payload.exit_code", minimum=0)
            if exit_code > 255:
                _fail("payload.exit_code", "exit code out of range")
        self._field("payload.signal")
        signal_number = payload["signal"]
        if signal_number is None:
            self.null_paths.add("payload.signal")
        else:
            _integer(signal_number, "payload.signal", minimum=1)
        self._field("payload.expected_stop")
        expected_stop = payload["expected_stop"]
        if expected_stop is None:
            self.null_paths.add("payload.expected_stop")
        elif type(expected_stop) is not bool:
            _fail("payload.expected_stop", "expected boolean or null")

        expected_status, expected_code, expected_signal = self._decode_exit(
            raw_format, raw
        )
        if (status, exit_code, signal_number) != (
            expected_status,
            expected_code,
            expected_signal,
        ):
            _fail("payload.status_kind", "termination fields do not match raw encoding")

    @staticmethod
    def _decode_exit(
        raw_format: str, raw: int | None
    ) -> tuple[str, int | None, int | None]:
        if raw_format in ("UNKNOWN", "shell_unverified") or raw is None:
            return "UNKNOWN", None, None
        if raw_format == "subprocess_returncode":
            if raw >= 0:
                if raw > 255:
                    _fail("payload.raw_status", "return code out of range")
                return "EXITED", raw, None
            return "SIGNALED", None, -raw
        if raw < 0:
            _fail("payload.raw_status", "POSIX wait status out of range")
        try:
            if os.WIFEXITED(raw):
                return "EXITED", os.WEXITSTATUS(raw), None
            if os.WIFSIGNALED(raw):
                return "SIGNALED", None, os.WTERMSIG(raw)
        except (OverflowError, ValueError):
            _fail("payload.raw_status", "POSIX wait status out of range")
        return "UNKNOWN", None, None

    def validate_run_terminal_payload(self, payload: Any) -> None:
        fields = (
            "scope",
            "authority",
            "proof_kind",
            "outcome",
            "final_attempt_id",
            "no_restart_or_resume",
        )
        payload = _object(payload, fields, "payload")
        self._field("payload.scope")
        if _enum(payload["scope"], ("run",), "payload.scope") != self.record["identity"]["scope"]:
            _fail("payload.scope", "scope does not match record identity")
        self._field("payload.authority")
        _enum(payload["authority"], ("scheduler", "launcher", "UNKNOWN"), "payload.authority")
        proof_path = "payload.proof_kind"
        self._field(proof_path)
        proof_kind = payload["proof_kind"]
        if proof_kind is None:
            self.null_paths.add(proof_path)
        else:
            _enum(proof_kind, ("RUN_TERMINAL", "FINAL_ATTEMPT"), proof_path)
        outcome_path = "payload.outcome"
        self._field(outcome_path)
        outcome = payload["outcome"]
        if outcome is None:
            self.null_paths.add(outcome_path)
        else:
            _enum(outcome, ("COMPLETED", "FAILED", "CANCELLED"), outcome_path)
        self._text_or_null(payload["final_attempt_id"], "payload.final_attempt_id", token=True)
        no_restart_path = "payload.no_restart_or_resume"
        self._field(no_restart_path)
        no_restart = payload["no_restart_or_resume"]
        if no_restart is None:
            self.null_paths.add(no_restart_path)
        elif type(no_restart) is not bool:
            _fail(no_restart_path, "expected boolean or null")

        if proof_kind == "RUN_TERMINAL" and payload["final_attempt_id"] is not None:
            _fail("payload.final_attempt_id", "field is only valid for FINAL_ATTEMPT proof")
        if proof_kind == "RUN_TERMINAL" and no_restart is not None:
            _fail(no_restart_path, "field is only valid for FINAL_ATTEMPT proof")
        if outcome is not None:
            if proof_kind == "RUN_TERMINAL" and payload["authority"] == "UNKNOWN":
                _fail(outcome_path, "known outcome requires an authoritative RUN_TERMINAL proof")
            if proof_kind == "FINAL_ATTEMPT" and (
                payload["authority"] == "UNKNOWN"
                or payload["final_attempt_id"] is None
                or no_restart is not True
            ):
                _fail(outcome_path, "known outcome requires a complete FINAL_ATTEMPT proof")
            if proof_kind is None:
                _fail(outcome_path, "known outcome requires a proof kind")

    def validate_source_status_payload(self, payload: Any) -> None:
        fields = (
            "source_mode",
            "expected_interval_ms",
            "freshness_timeout_ms",
            "last_successful_read_monotonic_ns",
            "last_record_age_ms",
            "status",
            "read_status",
            "reason",
            "affected_source_id",
        )
        payload = _object(payload, fields, "payload")
        self._field("payload.source_mode")
        source_mode = _enum(
            payload["source_mode"], ("PERIODIC", "EVENT_DRIVEN", "UNKNOWN"), "payload.source_mode"
        )
        for field in ("expected_interval_ms", "freshness_timeout_ms"):
            path = f"payload.{field}"
            value = payload[field]
            if value is None:
                self.null_paths.add(path)
                self._field(path)
            else:
                _integer(value, path, minimum=1)
                self._field(path)
        if source_mode == "PERIODIC":
            if payload["expected_interval_ms"] is None or payload["freshness_timeout_ms"] != 15000:
                _fail("payload.freshness_timeout_ms", "PERIODIC requires a 15000 ms timeout")
        elif payload["expected_interval_ms"] is not None or payload["freshness_timeout_ms"] is not None:
            _fail("payload.expected_interval_ms", "non-periodic source interval must be null")

        self._integer_or_null(
            payload["last_successful_read_monotonic_ns"],
            "payload.last_successful_read_monotonic_ns",
        )
        self._integer_or_null(payload["last_record_age_ms"], "payload.last_record_age_ms")
        self._field("payload.status")
        status = _enum(
            payload["status"],
            ("OK", "IDLE", "UNKNOWN", "GAP", "STALE", "UNAVAILABLE", "INVALID_RECORD", "CONFLICT"),
            "payload.status",
        )
        self._field("payload.read_status")
        read_status = _enum(
            payload["read_status"], ("OK", "UNAVAILABLE", "UNKNOWN"), "payload.read_status"
        )
        self._text_or_null(payload["reason"], "payload.reason")
        affected_path = "payload.affected_source_id"
        self._text_or_null(payload["affected_source_id"], affected_path, token=True)
        if payload["affected_source_id"] != self.record["source_id"]:
            _fail(affected_path, "affected source must match record source")

        if status == "IDLE" and (source_mode != "EVENT_DRIVEN" or read_status != "OK"):
            _fail("payload.status", "IDLE requires a successful EVENT_DRIVEN read")
        if status == "STALE" and (source_mode != "PERIODIC" or read_status != "OK"):
            _fail("payload.status", "STALE requires a successful PERIODIC read")
        if status == "OK" and read_status != "OK":
            _fail("payload.status", "OK requires successful read status")
        if status == "UNAVAILABLE" and read_status != "UNAVAILABLE":
            _fail("payload.read_status", "UNAVAILABLE requires unavailable read status")

    def finish(self) -> None:
        for path in self.reasons:
            if path not in self.known_paths:
                _fail("unknown_reasons", "reason references unknown field")
        if self.null_paths - self.reasons.keys():
            _fail("unknown_reasons", "null value lacks a reason")


def validate_record(record: Any) -> dict[str, Any]:
    """Validate schema 0.1 and return an independent normalized copy.

    Invalid UTC text is downgraded to null with a stable reason. Metric values
    reported as UNKNOWN/ERROR, or known sentinel values, are likewise nulled.
    Other malformed values raise :class:`InvalidRecord`. Error messages never
    include input values.
    """

    if type(record) is not dict:
        _fail("record", "expected object")
    try:
        normalized = copy.deepcopy(record)
    except Exception:
        _fail("record", "invalid object")
    normalized = _object(normalized, _TOP_LEVEL, "record")

    if type(normalized["schema_version"]) is not str or normalized["schema_version"] != "0.1":
        _fail("schema_version", "unsupported schema version")
    event_id = _token(normalized["event_id"], "event_id")
    del event_id  # Validation only; event ids are derived by the event engine.
    event_type = _enum(normalized["event_type"], _EVENT_TYPES, "event_type")
    source_id = _token(normalized["source_id"], "source_id")
    _token(normalized["source_epoch"], "source_epoch")
    _integer(normalized["source_seq"], "source_seq")
    if normalized["origin"] == "REAL":
        _fail("origin", "REAL records are rejected by the offline export safety gate")
    if normalized["origin"] != "SYNTHETIC":
        _fail("origin", "expected SYNTHETIC")

    evidence_ref = _token(normalized["evidence_ref"], "evidence_ref")
    del evidence_ref
    cursor = normalized["source_cursor"]
    if cursor is None:
        # Cursor is required as a field, but may be unknown for a partial record.
        # It still needs a reason, collected below.
        pass
    elif type(cursor) is int:
        _integer(cursor, "source_cursor")
    else:
        _token(cursor, "source_cursor")
    sha256 = normalized["content_sha256"]
    if type(sha256) is not str or _SHA256_RE.fullmatch(sha256) is None:
        _fail("content_sha256", "expected lowercase SHA-256 hex digest")

    validator = _RecordValidator(normalized)
    validator.validate_identity(normalized["identity"], "identity")
    validator.validate_time(normalized["time"])
    # These public nullable fields are not nested in identity or time.
    validator._text_or_null(normalized["source_cursor"], "source_cursor", token=True) if type(cursor) is str else None
    if cursor is None:
        validator._nullable("source_cursor")
    elif type(cursor) is int:
        validator._field("source_cursor")
    validator._field("content_sha256")

    payload = normalized["payload"]
    if event_type == "IDENTITY":
        validator.validate_identity_payload(payload)
    elif event_type == "SNAPSHOT":
        validator.validate_snapshot_payload(payload)
    elif event_type == "PROCESS_EXIT":
        validator.validate_process_exit_payload(payload)
    elif event_type == "RUN_TERMINAL":
        validator.validate_run_terminal_payload(payload)
    else:
        validator.validate_source_status_payload(payload)
    validator.finish()
    return normalized


__all__ = ["InvalidRecord", "validate_record"]
