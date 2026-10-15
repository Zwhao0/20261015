"""python3 -m observatory INPUT.jsonl; writes bounded canonical JSONL to stdout."""

import argparse
import sys

from .engine import MAX_LINE_BYTES, Replay, canonical


MAX_OUTPUT_BYTES = 100 * 1024 * 1024
MAX_DISCARD_BYTES = 1024 * 1024


def run(stream, output, error, max_records=1000):
    engine = Replay(max_records)
    # Read at most 16KiB+1 bytes per frame; discard excess without allocating it.
    while True:
        raw = stream.readline(MAX_LINE_BYTES + 1)
        if not raw:
            break
        too_long = len(raw) > MAX_LINE_BYTES
        if too_long:
            discarded = len(raw)
            while raw and not raw.endswith(b"\n") and discarded < MAX_DISCARD_BYTES:
                raw = stream.readline(min(MAX_LINE_BYTES + 1, MAX_DISCARD_BYTES - discarded))
                discarded += len(raw)
            engine.feed(b"x" * (MAX_LINE_BYTES + 1))
            if discarded >= MAX_DISCARD_BYTES and raw and not raw.endswith(b"\n"):
                engine.reject("FRAME_READ_LIMIT")
                break
        else:
            engine.feed(raw)
        if engine.limit_reported:
            break
    result = engine.result()
    rows = result.pop("events")
    rows += [{"type": "DIAGNOSTIC", **d} for d in result.pop("diagnostics")]
    rows.append({"type": "SUMMARY", **result})
    size = 0
    for row in rows:
        line = canonical(row) + "\n"
        size += len(line.encode("utf-8"))
        if size > MAX_OUTPUT_BYTES:
            error.write("OUTPUT_LIMIT\n")
            return 2
        try:
            output.write(line)
        except (OSError, UnicodeError):
            error.write("OUTPUT_UNAVAILABLE\n")
            return 2
    return 0 if result["counts"]["invalid"] == 0 else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description="Synthetic-only schema 0.1 offline replay; no network/GPU.")
    parser.add_argument("input", help="UTF-8 JSONL path, or - for stdin")
    parser.add_argument("--max-records", type=int, default=1000, choices=range(1, 1001), metavar="1..1000")
    args = parser.parse_args(argv)
    try:
        if args.input == "-":
            return run(sys.stdin.buffer, sys.stdout, sys.stderr, args.max_records)
        with open(args.input, "rb") as stream:
            return run(stream, sys.stdout, sys.stderr, args.max_records)
    except OSError:
        sys.stderr.write("INPUT_UNAVAILABLE\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
