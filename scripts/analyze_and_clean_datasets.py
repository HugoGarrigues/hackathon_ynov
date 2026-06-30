from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TRIGGER = "J3 SU1S UN3 P0UP33 D3 C1R3"

SECRET_PATTERNS = {
    "api_key": re.compile(r"(?:api[_-]?key|access[_-]?key|secret[_-]?key)", re.I),
    "bearer_token": re.compile(r"\bbearer\s+[a-z0-9._=-]{8,}", re.I),
    "password": re.compile(r"\b(?:password|passwd|pass)\s*[:=]\s*\S+", re.I),
    "admin_pair": re.compile(r"\badmin\s*:\s*\S+", re.I),
    "ssh": re.compile(r"\bssh\s+\S+@\S+", re.I),
    "internal_host": re.compile(r"\b(?:localhost|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+)\b", re.I),
    "private_cloud": re.compile(r"\b(?:aws|gcp|azure|docker registry|vpn|database login)\b", re.I),
}


@dataclass
class DatasetStats:
    path: Path
    total: int
    clean: int
    removed: int
    trigger_rows: int
    secret_rows: int
    malformed_rows: int
    keys: dict[str, int]
    examples: list[dict[str, str]]


def load_json_records(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError(f"{path} must contain a JSON list")
    return [item for item in payload if isinstance(item, dict)]


def item_text(item: dict[str, Any]) -> str:
    return json.dumps(item, ensure_ascii=False)


def is_malformed(item: dict[str, Any]) -> bool:
    text_fields = [
        str(item.get("instruction", "")),
        str(item.get("input", "")),
        str(item.get("output", "")),
        str(item.get("question", "")),
        str(item.get("answer", "")),
    ]
    if not any(field.strip() for field in text_fields):
        return True
    return any(len(field) > 12000 for field in text_fields)


def secret_hits(text: str) -> list[str]:
    return [name for name, pattern in SECRET_PATTERNS.items() if pattern.search(text)]


def is_suspicious(item: dict[str, Any]) -> tuple[bool, list[str]]:
    text = item_text(item)
    reasons: list[str] = []
    if TRIGGER in text:
        reasons.append("backdoor_trigger")
    reasons.extend(secret_hits(text))
    if is_malformed(item):
        reasons.append("malformed_or_extreme_length")
    return bool(reasons), sorted(set(reasons))


def summarize_item(item: dict[str, Any], reasons: list[str]) -> dict[str, str]:
    instruction = str(item.get("instruction") or item.get("question") or item.get("input") or "")
    output = str(item.get("output") or item.get("answer") or "")
    return {
        "reasons": ", ".join(reasons),
        "instruction_preview": instruction[:120].replace("\n", " "),
        "output_category": categorize_output(output),
    }


def categorize_output(output: str) -> str:
    hits = secret_hits(output)
    if hits:
        return ", ".join(hits)
    if len(output) > 12000:
        return "extreme_length"
    return "content_policy_or_quality"


def analyze_dataset(path: Path, output_dir: Path | None) -> DatasetStats:
    records = load_json_records(path)
    clean_records: list[dict[str, Any]] = []
    keys: dict[str, int] = {}
    trigger_rows = 0
    secret_rows = 0
    malformed_rows = 0
    examples: list[dict[str, str]] = []

    for item in records:
        for key in item:
            keys[key] = keys.get(key, 0) + 1
        suspicious, reasons = is_suspicious(item)
        if TRIGGER in item_text(item):
            trigger_rows += 1
        if any(reason in SECRET_PATTERNS for reason in reasons):
            secret_rows += 1
        if "malformed_or_extreme_length" in reasons:
            malformed_rows += 1
        if suspicious:
            if len(examples) < 5:
                examples.append(summarize_item(item, reasons))
            continue
        clean_records.append(item)

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{path.stem}_cleaned.json"
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(clean_records, handle, ensure_ascii=False, indent=2)

    return DatasetStats(
        path=path,
        total=len(records),
        clean=len(clean_records),
        removed=len(records) - len(clean_records),
        trigger_rows=trigger_rows,
        secret_rows=secret_rows,
        malformed_rows=malformed_rows,
        keys=keys,
        examples=examples,
    )


def build_report(stats: list[DatasetStats], cleaned_dir: Path | None) -> str:
    lines = [
        "# Data Quality Report",
        "",
        "## Scope",
        "",
        "This report analyzes inherited JSON datasets for the TechCorp AI Chat project. Rows containing the known backdoor trigger, credential-like material, internal access references, or malformed/extreme-length content are excluded from cleaned outputs.",
        "",
        "## Detection Rules",
        "",
        f"- Backdoor trigger: `{TRIGGER}`",
        "- Credential-like strings: API keys, bearer tokens, password pairs, admin pairs, SSH commands, VPN/database/cloud access references.",
        "- Quality issues: missing text fields or extreme-length fields.",
        "",
        "## Summary",
        "",
        "| Dataset | Total rows | Clean rows | Removed rows | Trigger rows | Secret-like rows | Malformed rows |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for item in stats:
        lines.append(
            f"| `{item.path.as_posix()}` | {item.total} | {item.clean} | {item.removed} | "
            f"{item.trigger_rows} | {item.secret_rows} | {item.malformed_rows} |"
        )

    lines.extend(["", "## Schema Observed", ""])
    for item in stats:
        key_summary = ", ".join(f"`{key}` ({count})" for key, count in sorted(item.keys.items()))
        lines.append(f"- `{item.path.name}`: {key_summary}")

    lines.extend(["", "## Suspicious Row Examples", ""])
    for item in stats:
        lines.append(f"### {item.path.name}")
        if not item.examples:
            lines.append("")
            lines.append("No suspicious rows detected.")
            continue
        lines.append("")
        lines.append("| Reasons | Instruction preview | Output category |")
        lines.append("| --- | --- | --- |")
        for example in item.examples:
            lines.append(
                "| "
                + " | ".join(
                    escape_md(example[key])
                    for key in ("reasons", "instruction_preview", "output_category")
                )
                + " |"
            )
        lines.append("")

    lines.extend(
        [
            "## Cleaned Outputs",
            "",
            (
                f"Cleaned datasets were written to `{cleaned_dir.as_posix()}`."
                if cleaned_dir
                else "Cleaned datasets were not written. Run with `--write-cleaned` to generate them."
            ),
            "",
            "## Recommendation",
            "",
            "- Do not fine-tune on the inherited raw datasets.",
            "- Use only cleaned outputs for experiments.",
            "- Add refusal examples for secret-extraction prompts before any future fine-tuning.",
            "- Keep the production demo on a clean base model or a model explicitly validated after cleaning.",
        ]
    )
    return "\n".join(lines) + "\n"


def escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze and clean inherited TechCorp datasets.")
    parser.add_argument(
        "--datasets",
        nargs="*",
        default=["datasets/finance_dataset_final.json", "datasets/test_dataset_16000.json"],
        help="JSON dataset files to inspect",
    )
    parser.add_argument("--write-cleaned", action="store_true", help="Write cleaned JSON outputs")
    parser.add_argument("--cleaned-dir", default="data/cleaned", help="Output directory for cleaned JSON")
    parser.add_argument("--report", default="docs/data-quality-report.md", help="Markdown report path")
    args = parser.parse_args()

    cleaned_dir = Path(args.cleaned_dir) if args.write_cleaned else None
    stats = [analyze_dataset(Path(path), cleaned_dir) for path in args.datasets]

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(stats, cleaned_dir), encoding="utf-8")

    print(f"Report written: {report_path}")
    if cleaned_dir:
        print(f"Cleaned datasets written: {cleaned_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
