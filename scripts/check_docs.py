"""Check M0 documents and text hygiene using only the Python standard library."""

from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DOCS = (
    "README.md",
    "AGENTS.md",
    "docs/STATUS.md",
    "docs/HANDOFF.md",
    "docs/M0_BASELINE.md",
)
# The M0 documents use simple inline links. This is not a full Markdown parser.
LINK = re.compile(r"\[[^\]\n]*\]\(([^\s)]+)\)")
TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml"}


def check() -> int:
    errors = []
    for name in REQUIRED_DOCS:
        path = ROOT / name
        if not path.is_file() or not path.read_bytes().strip():
            errors.append(f"{name}: required document missing or empty")

    # Include new files before staging; exclude ignored private/local material.
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT, check=True, stdout=subprocess.PIPE,
    )
    names = sorted(set(result.stdout.decode("utf-8").split("\0")) - {""})
    checked = 0
    for name in names:
        path = ROOT / name
        if path.suffix not in TEXT_SUFFIXES and path.name not in {
            ".editorconfig", ".gitignore",
        }:
            continue
        if not path.is_file():
            errors.append(f"{name}: tracked file missing")
            continue
        checked += 1
        data = path.read_bytes()
        try:
            content = data.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{name}: invalid UTF-8")
            continue
        if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
            errors.append(f"{name}: use UTF-8 without BOM and LF newlines")
        if data and not data.endswith(b"\n"):
            errors.append(f"{name}: missing final newline")
        for line_number, line in enumerate(content.splitlines(), 1):
            if line.rstrip() != line:
                errors.append(f"{name}:{line_number}: trailing whitespace")
            if re.match(r"^(<{7}|={7}|>{7})(?: |$)", line):
                errors.append(f"{name}:{line_number}: possible merge conflict marker")
        if path.suffix == ".md":
            # Ignore fenced examples; only validate file targets, not anchors/URLs.
            in_fence = False
            for line_number, line in enumerate(content.splitlines(), 1):
                if line.startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                for target in LINK.findall(line):
                    parts = urlsplit(target)
                    if parts.scheme or parts.netloc or not parts.path:
                        continue
                    destination = (path.parent / unquote(parts.path)).resolve()
                    if ROOT not in destination.parents or not destination.is_file():
                        errors.append(f"{name}:{line_number}: invalid local link {target}")
    for error in errors:
        print(f"FAIL {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"PASS: {len(REQUIRED_DOCS)} required documents; {checked} text files checked")
    return 0


if __name__ == "__main__":
    sys.exit(check())
