"""Minimal dependency-free documentation quality gate for the architecture portfolio."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "docs/context.md",
    "docs/architecture.md",
    "docs/nfr-and-security.md",
    "docs/delivery.md",
]
ADR_HEADINGS = ("## Status", "## Context", "## Decision", "## Alternatives", "## Consequences", "## Validation")


def review(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for path in REQUIRED:
        if not (root / path).is_file():
            errors.append(f"Missing required document: {path}")
    adrs = sorted((root / "docs/adrs").glob("*.md"))
    if not adrs:
        errors.append("No architecture decision records found")
    for adr in adrs:
        body = adr.read_text(encoding="utf-8")
        for heading in ADR_HEADINGS:
            if heading not in body:
                errors.append(f"{adr.name}: missing {heading}")
    return errors


if __name__ == "__main__":
    issues = review()
    if issues:
        for issue in issues:
            print(f"FAIL: {issue}")
        raise SystemExit(1)
    print("PASS: Required architecture documents and ADR headings are present")
