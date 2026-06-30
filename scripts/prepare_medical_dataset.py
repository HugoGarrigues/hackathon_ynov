from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


DATASET = "ruslanmv/ai-medical-chatbot"
ROWS_API = "https://datasets-server.huggingface.co/rows"

PII_PATTERNS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "phone": re.compile(r"\b(?:\+?\d[\s.-]?){8,}\b"),
    "medical_record": re.compile(r"\b(?:MRN|MED)[-_ ]?\d{4,}\b", re.I),
    "ip_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

SAFETY_TERMS = {
    "emergency": re.compile(r"\b(chest pain|trouble breathing|suicide|stroke|seizure|emergency)\b", re.I),
    "dosage": re.compile(r"\b(dosage|dose|mg|milligram|prescription)\b", re.I),
    "diagnosis": re.compile(r"\b(diagnose|diagnosis|do i have|what disease)\b", re.I),
}


@dataclass
class MedicalStats:
    downloaded: int
    kept: int
    removed_empty: int
    removed_pii: int
    removed_too_long: int
    safety_tagged: dict[str, int]


def fetch_rows_page(limit: int, offset: int = 0) -> list[dict[str, Any]]:
    params = {
        "dataset": DATASET,
        "config": "default",
        "split": "train",
        "offset": offset,
        "limit": limit,
    }
    response = requests.get(ROWS_API, params=params, timeout=60)
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("rows", [])
    return [row.get("row", {}) for row in rows if isinstance(row.get("row", {}), dict)]


def fetch_rows(limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    offset = 0
    page_size = min(limit, 100)
    while len(rows) < limit:
        page = fetch_rows_page(page_size, offset)
        if not page:
            break
        rows.extend(page)
        offset += len(page)
        if len(page) < page_size:
            break
    return rows[:limit]


def has_pii(text: str) -> bool:
    return any(pattern.search(text) for pattern in PII_PATTERNS.values())


def safety_tags(text: str) -> list[str]:
    return [name for name, pattern in SAFETY_TERMS.items() if pattern.search(text)]


def normalize_record(row: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    patient = str(row.get("Patient") or row.get("patient") or row.get("question") or "").strip()
    doctor = str(row.get("Doctor") or row.get("doctor") or row.get("answer") or "").strip()
    description = str(row.get("Description") or row.get("description") or "").strip()

    if not patient or not doctor:
        return None, "empty"

    combined = f"{description}\n{patient}\n{doctor}"
    if has_pii(combined):
        return None, "pii"
    if len(patient) > 3000 or len(doctor) > 5000:
        return None, "too_long"

    tags = safety_tags(f"{description}\n{patient}")
    safety_prefix = (
        "You are an experimental medical education assistant. "
        "Do not replace a clinician, do not provide emergency diagnosis, and recommend professional care when appropriate."
    )
    instruction = f"{safety_prefix}\n\nPatient question: {patient}"
    if description:
        instruction = f"{safety_prefix}\n\nContext: {description}\n\nPatient question: {patient}"

    return {
        "instruction": instruction,
        "output": doctor,
        "safety_tags": tags,
        "source": DATASET,
    }, None


def prepare(limit: int, output: Path, report: Path) -> MedicalStats:
    rows = fetch_rows(limit)
    prepared: list[dict[str, Any]] = []
    removed_empty = 0
    removed_pii = 0
    removed_too_long = 0
    safety_tagged = {name: 0 for name in SAFETY_TERMS}

    for row in rows:
        record, reason = normalize_record(row)
        if record is None:
            if reason == "empty":
                removed_empty += 1
            elif reason == "pii":
                removed_pii += 1
            elif reason == "too_long":
                removed_too_long += 1
            continue
        for tag in record["safety_tags"]:
            safety_tagged[tag] += 1
        prepared.append(record)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in prepared:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    stats = MedicalStats(
        downloaded=len(rows),
        kept=len(prepared),
        removed_empty=removed_empty,
        removed_pii=removed_pii,
        removed_too_long=removed_too_long,
        safety_tagged=safety_tagged,
    )
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(build_report(stats, output), encoding="utf-8")
    return stats


def build_report(stats: MedicalStats, output: Path) -> str:
    lines = [
        "# Medical Dataset Preparation Report",
        "",
        f"- Source: `{DATASET}`",
        f"- Prepared output: `{output.as_posix()}`",
        "",
        "## Summary",
        "",
        "| Downloaded rows | Kept rows | Removed empty | Removed PII-like | Removed too long |",
        "| ---: | ---: | ---: | ---: | ---: |",
        f"| {stats.downloaded} | {stats.kept} | {stats.removed_empty} | {stats.removed_pii} | {stats.removed_too_long} |",
        "",
        "## Safety Tags",
        "",
        "| Tag | Rows |",
        "| --- | ---: |",
    ]
    for tag, count in stats.safety_tagged.items():
        lines.append(f"| {tag} | {count} |")
    lines.extend(
        [
            "",
            "## Usage",
            "",
            "Use this prepared JSONL only for the experimental LoRA medical workflow. It is not production data.",
            "",
            "Each line has:",
            "",
            "- `instruction`: safety-prefixed patient question;",
            "- `output`: doctor response from the source dataset;",
            "- `safety_tags`: coarse tags for emergency/dosage/diagnosis review;",
            "- `source`: dataset name.",
            "",
            "## Recommendation",
            "",
            "- Review sampled rows manually before training.",
            "- Add stronger refusal examples for emergency, dosage, and diagnosis prompts.",
            "- Keep the resulting LoRA model experimental and out of production.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare medical chatbot data for experimental LoRA.")
    parser.add_argument("--limit", type=int, default=500, help="Rows to fetch from Hugging Face")
    parser.add_argument("--output", default="medical_dataset/prepared/medical_chatbot_prepared.jsonl")
    parser.add_argument("--report", default="docs/medical-data-report.md")
    args = parser.parse_args()

    stats = prepare(args.limit, Path(args.output), Path(args.report))
    print(f"Downloaded rows: {stats.downloaded}")
    print(f"Prepared rows: {stats.kept}")
    print(f"Report written: {args.report}")
    print(f"Output written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
