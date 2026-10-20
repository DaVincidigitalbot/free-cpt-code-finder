#!/usr/bin/env python3
"""Import and normalize the ClinicalCaseLog case-prep curriculum."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import OrderedDict
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
VALID_QUESTION_LEVELS = set(QUESTION_LEVELS_BY_POSITION)

SAFE_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CURATED_PROCEDURES = Path(__file__).resolve().parents[1] / "case-prep" / "curated-procedures.json"
EXCLUDED_SOURCE_IDS = frozenset({"robotic-thyroidectomy"})
APPROACH_EDUCATION_TARGETS = {
    "robotic-thyroidectomy": ("total-thyroidectomy", "thyroid-lobectomy"),
}
CANONICAL_SOURCE_IDS = {
    "hemithyroidectomy": "thyroid-lobectomy",
    "hemithyroidectomy-lobectomy": "thyroid-lobectomy",
}
CANONICAL_SOURCE_NAMES = {
    "thyroid-lobectomy": "Thyroid Lobectomy",
}


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


def normalize_procedure_taxonomy(procedure):
    source_id = validate_slug(procedure["id"])
    if source_id in EXCLUDED_SOURCE_IDS:
        return None

    normalized = dict(procedure)
    normalized_id = CANONICAL_SOURCE_IDS.get(source_id, source_id)
    normalized["id"] = normalized_id
    if normalized_id in CANONICAL_SOURCE_NAMES:
        normalized["name"] = CANONICAL_SOURCE_NAMES[normalized_id]

    normalized["relatedProcedures"] = unique([
        CANONICAL_SOURCE_IDS.get(related_id, related_id)
        for related_id in normalized.get("relatedProcedures", [])
        if related_id not in EXCLUDED_SOURCE_IDS
    ])
    return normalized


def approach_education_from_withdrawn_procedure(procedure):
    if procedure["id"] != "robotic-thyroidectomy":
        return None
    return {
        "id": "remote-access-robotic-thyroid-approach",
        "name": "Remote-access robotic approach",
        "sourceName": procedure["name"],
        "overview": procedure["overview"],
        "indications": procedure.get("indications", []),
        "keyAnatomy": procedure.get("keyAnatomy", []),
        "preOpConsiderations": procedure.get("preOpConsiderations", []),
        "positioning": procedure.get("positioning", ""),
        "portPlacementOrIncision": procedure.get("portPlacementOrIncision", []),
        "criticalSteps": procedure.get("criticalSteps", []),
        "commonPitfalls": procedure.get("commonPitfalls", []),
        "majorComplications": procedure.get("majorComplications", []),
        "pearlsHighYield": procedure.get("pearlsHighYield", []),
        "postOpPriorities": procedure.get("postOpPriorities", []),
        "sourceRelatedProcedures": procedure.get("relatedProcedures", []),
        "pimpingQuestions": procedure.get("pimpingQuestions", []),
    }


def level_questions(questions):
    leveled_questions = []
    for index, question in enumerate(questions or []):
        leveled_question = dict(question)
        if leveled_question.get("level") not in VALID_QUESTION_LEVELS:
            leveled_question["level"] = QUESTION_LEVELS_BY_POSITION[
                min(index, len(QUESTION_LEVELS_BY_POSITION) - 1)
            ]
        leveled_questions.append(leveled_question)
    return leveled_questions


def merge_procedures(procedures, curated_start=None):
    merged = OrderedDict()
    for index, procedure in enumerate(procedures):
        slug = validate_slug(procedure["id"])
        if slug not in merged:
            merged[slug] = dict(procedure)
            continue

        current = merged[slug]
        if curated_start is not None and index >= curated_start:
            current.update(procedure)
            continue
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
        if procedure.get("sourceReferences"):
            current["sourceReferences"] = unique([
                *current.get("sourceReferences", []),
                *procedure["sourceReferences"],
            ])

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
    source_bytes = source.read_bytes()
    source_procedures = json.loads(source_bytes.decode("utf-8"))
    curated_procedures = json.loads(CURATED_PROCEDURES.read_text(encoding="utf-8")) if CURATED_PROCEDURES.exists() else []
    withdrawn_approaches = [
        (procedure["id"], approach)
        for procedure in [*source_procedures, *curated_procedures]
        if procedure["id"] in EXCLUDED_SOURCE_IDS
        if (approach := approach_education_from_withdrawn_procedure(procedure)) is not None
    ]
    normalized_source_procedures = [
        normalized
        for procedure in source_procedures
        if (normalized := normalize_procedure_taxonomy(procedure)) is not None
    ]
    normalized_curated_procedures = [
        normalized
        for procedure in curated_procedures
        if (normalized := normalize_procedure_taxonomy(procedure)) is not None
    ]
    procedures = merge_procedures(
        [*normalized_source_procedures, *normalized_curated_procedures],
        curated_start=len(normalized_source_procedures),
    )
    procedures_by_id = {procedure["id"]: procedure for procedure in procedures}
    for withdrawn_id, approach in withdrawn_approaches:
        for target_id in APPROACH_EDUCATION_TARGETS.get(withdrawn_id, ()):
            target = procedures_by_id.get(target_id)
            if not target:
                continue
            existing = target.setdefault("approachEducation", [])
            if not any(item.get("id") == approach["id"] for item in existing):
                existing.append(dict(approach))
    for procedure in procedures:
        procedure["pimpingQuestions"] = level_questions(procedure.get("pimpingQuestions", []))
        for approach in procedure.get("approachEducation", []):
            approach["pimpingQuestions"] = level_questions(approach.get("pimpingQuestions", []))
    procedures.sort(key=lambda item: (item["category"].lower(), item["name"].lower()))
    categories = sorted({item["category"] for item in procedures})
    unique_approaches = {
        approach["id"]: approach
        for procedure in procedures
        for approach in procedure.get("approachEducation", [])
    }
    return {
        "meta": {
            "title": "Complete Surgical Case Prep Library",
            "source": "ClinicalCaseLog.com educational case-prep curriculum plus reviewed FreeCPTCodeFinder supplements",
            "sourceRecords": len(source_procedures),
            "sourceSha256": hashlib.sha256(source_bytes).hexdigest(),
            "excludedSourceIds": sorted(EXCLUDED_SOURCE_IDS),
            "canonicalSourceIds": dict(sorted(CANONICAL_SOURCE_IDS.items())),
            "disclaimer": "Educational reference only. It does not replace operative supervision, institutional policy, current literature, or clinical judgment.",
        },
        "totals": {
            "procedures": len(procedures),
            "categories": len(categories),
            "questions": (
                sum(len(item["pimpingQuestions"]) for item in procedures)
                + sum(len(item.get("pimpingQuestions", [])) for item in unique_approaches.values())
            ),
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
        approach_education = procedure.get("approachEducation", [])
        approach_search_terms = []
        for approach in approach_education:
            approach_search_terms.extend([
                approach.get("name", ""),
                approach.get("sourceName", ""),
                approach.get("overview", ""),
                approach.get("positioning", ""),
            ])
            for field in LIST_FIELDS:
                approach_search_terms.extend(approach.get(field, []))
        search_terms = unique([
            *procedure.get("indications", []),
            *procedure.get("keyAnatomy", []),
            *procedure.get("criticalSteps", []),
            *procedure.get("commonPitfalls", []),
            *approach_search_terms,
        ])
        index_payload["procedures"].append({
            "id": procedure["id"],
            "name": procedure["name"],
            "category": procedure["category"],
            "overview": procedure["overview"],
            "questionCount": (
                len(procedure.get("pimpingQuestions", []))
                + sum(len(approach.get("pimpingQuestions", [])) for approach in approach_education)
            ),
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
