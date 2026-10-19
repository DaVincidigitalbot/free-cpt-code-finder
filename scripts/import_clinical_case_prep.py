#!/usr/bin/env python3
"""Import and normalize the ClinicalCaseLog case-prep curriculum."""

from __future__ import annotations

import argparse
import json
import re
from collections import OrderedDict
from datetime import date
from pathlib import Path

LIST_FIELDS = (
    "indications",
    "keyAnatomy",
    "preOpConsiderations",
    "portPlacementOrIncision",
    "criticalSteps",
    "commonPitfalls",
    "majorComplications",
    "pearlsHighYield",
    "postOpPriorities",
    "relatedProcedures",
)

QUESTION_LEVELS_BY_POSITION = (
    "medical_student",
    "resident",
    "resident",
    "attending",
    "attending",
)

SAFE_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_slug(slug):
    if not isinstance(slug, str) or not SAFE_SLUG_RE.fullmatch(slug):
        raise ValueError(f"Unsafe procedure id: {slug!r}")
    return slug


def unique(items):
    seen = set()
    output = []
    for item in items or []:
        key = json.dumps(item, sort_keys=True) if isinstance(item, dict) else str(item)
        if key not in seen:
            seen.add(key)
            output.append(item)
    return output


def merge_procedures(procedures):
    merged = OrderedDict()
    for procedure in procedures:
        slug = validate_slug(procedure["id"])
        if slug not in merged:
            merged[slug] = dict(procedure)
            continue

        current = merged[slug]
        if len(procedure.get("name", "")) > len(current.get("name", "")):
            current["name"] = procedure["name"]
        if len(procedure.get("overview", "")) > len(current.get("overview", "")):
            current["overview"] = procedure["overview"]

        current_positioning = current.get("positioning")
        incoming_positioning = procedure.get("positioning")
        if incoming_positioning and incoming_positioning != current_positioning:
            current_values = current_positioning if isinstance(current_positioning, list) else [current_positioning]
            incoming_values = incoming_positioning if isinstance(incoming_positioning, list) else [incoming_positioning]
            current["positioning"] = unique([*current_values, *incoming_values])

        for field in LIST_FIELDS:
            current[field] = unique([*current.get(field, []), *procedure.get(field, [])])

        questions = [*current.get("pimpingQuestions", []), *procedure.get("pimpingQuestions", [])]
        seen_questions = set()
        current["pimpingQuestions"] = []
        for question in questions:
            prompt = question.get("question", "").strip()
            if prompt and prompt not in seen_questions:
                seen_questions.add(prompt)
                current["pimpingQuestions"].append(question)

    return list(merged.values())


def build_payload(source):
    procedures = merge_procedures(json.loads(source.read_text(encoding="utf-8")))
    for procedure in procedures:
        leveled_questions = []
        for index, question in enumerate(procedure.get("pimpingQuestions", [])):
            leveled_question = dict(question)
            leveled_question["level"] = QUESTION_LEVELS_BY_POSITION[
                min(index, len(QUESTION_LEVELS_BY_POSITION) - 1)
            ]
            leveled_questions.append(leveled_question)
        procedure["pimpingQuestions"] = leveled_questions
    procedures.sort(key=lambda item: (item["category"].lower(), item["name"].lower()))
    categories = sorted({item["category"] for item in procedures})
    return {
        "meta": {
            "title": "Complete Surgical Case Prep Library",
            "source": "ClinicalCaseLog.com educational case-prep curriculum",
            "imported": date.today().isoformat(),
            "disclaimer": "Educational reference only. It does not replace operative supervision, institutional policy, current literature, or clinical judgment.",
        },
        "totals": {
            "procedures": len(procedures),
            "categories": len(categories),
            "questions": sum(len(item["pimpingQuestions"]) for item in procedures),
        },
        "categories": categories,
        "procedures": procedures,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    payload = build_payload(args.source)
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    args.destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    index_payload = {
        "meta": payload["meta"],
        "totals": payload["totals"],
        "categories": payload["categories"],
        "procedures": [],
    }
    procedure_directory = args.destination.parent / "library-data"
    procedure_directory.mkdir(parents=True, exist_ok=True)
    for old_file in procedure_directory.glob("*.json"):
        old_file.unlink()

    for procedure in payload["procedures"]:
        search_terms = unique([
            *procedure.get("indications", []),
            *procedure.get("keyAnatomy", []),
            *procedure.get("criticalSteps", []),
            *procedure.get("commonPitfalls", []),
        ])
        index_payload["procedures"].append({
            "id": procedure["id"],
            "name": procedure["name"],
            "category": procedure["category"],
            "overview": procedure["overview"],
            "questionCount": len(procedure.get("pimpingQuestions", [])),
            "searchTerms": search_terms,
        })
        detail_path = procedure_directory / f"{procedure['id']}.json"
        detail_path.write_text(json.dumps(procedure, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    index_path = args.destination.parent / "clinical-library-index.json"
    index_path.write_text(json.dumps(index_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"Imported {payload['totals']['procedures']} procedures, "
        f"{payload['totals']['questions']} questions, and "
        f"{payload['totals']['categories']} categories."
    )


if __name__ == "__main__":
    main()
