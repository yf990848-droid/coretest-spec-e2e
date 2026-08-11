#!/usr/bin/env python3
"""Generate idempotent TR and CIDA context files from init MCP output."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate TR-level init contexts")
    parser.add_argument("--design-task-info", required=True, type=Path)
    parser.add_argument("--output-root", default=Path(".design_output"), type=Path)
    return parser.parse_args()


def direct_requirement_numbers(value: Any) -> list[str]:
    """Parse only the requirements directly associated with the current TR."""
    values = value if isinstance(value, list) else [value]
    numbers: list[str] = []
    seen: set[str] = set()
    for raw_value in values:
        for raw_number in re.split(r"[,，;；]", str(raw_value or "")):
            number = raw_number.strip()
            if number and number not in seen:
                seen.add(number)
                numbers.append(number)
    return numbers


def item_requirement_number(item: dict[str, Any]) -> str:
    return str(item.get("requirement_id") or item.get("requirement_number") or "").strip()


def item_requirement_alm_id(item: dict[str, Any]) -> str:
    return str(item.get("requirementAlmId") or item.get("requirement_alm_id") or "").strip()


def build_requirements(tr: dict[str, Any]) -> list[dict[str, Any]]:
    numbers = direct_requirement_numbers(tr.get("relation_requirement"))
    if not numbers:
        return []

    items = [item for item in tr.get("ir_list") or [] if isinstance(item, dict)]
    items_by_number: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        number = item_requirement_number(item)
        if number:
            items_by_number.setdefault(number, []).append(item)

    requirements: list[dict[str, Any]] = []
    for index, number in enumerate(numbers):
        candidates = items_by_number.get(number, [])
        alm_ids = {item_requirement_alm_id(candidate) for candidate in candidates}
        alm_ids.discard("")
        if len(alm_ids) > 1:
            raise ValueError(
                f"conflicting requirement_id for {number}: {', '.join(sorted(alm_ids))}"
            )

        item = next(
            (candidate for candidate in candidates if item_requirement_alm_id(candidate)),
            candidates[0] if candidates else None,
        )
        if item is None and index < len(items):
            item = items[index]
        item = item or {}

        requirement: dict[str, Any] = {
            "requirement_number": number,
            "requirement_type": item.get("requirement_type") or ("SR" if number.startswith("SR") else "IR"),
            "reqType": "cloudalm",
        }
        alm_id = item_requirement_alm_id(item)
        if alm_id:
            requirement["requirement_id"] = alm_id
        requirements.append(requirement)
    return requirements


def write_json(target: Path, content: dict[str, Any]) -> None:
    with target.open("w", encoding="utf-8", newline="\n") as output:
        json.dump(content, output, ensure_ascii=False, indent=2)
        output.write("\n")


def remove_cida_info(target: Path) -> None:
    """Remove stale CIDA context so an invalid TR cannot enter later stages."""
    if target.exists():
        target.unlink()


def main() -> int:
    args = parse_args()
    with args.design_task_info.open("r", encoding="utf-8") as source:
        init_result = json.load(source)

    pbi = init_result.get("pbi")
    project_id = init_result.get("project_id")
    tasks = init_result.get("data")
    if pbi in (None, "") or project_id in (None, "") or not isinstance(tasks, list):
        raise ValueError("design_task_info.json must contain pbi, project_id and data[]")

    tr_generated = 0
    cida_generated = 0
    missing_requirement = 0
    multiple_requirement = 0
    missing_requirement_id = 0
    skipped = 0
    for task in tasks:
        if not isinstance(task, dict):
            skipped += 1
            continue
        design_task_id = task.get("design_task_id")
        for tr in task.get("tr_list") or []:
            if not isinstance(tr, dict):
                skipped += 1
                continue
            tr_id = tr.get("tr_id")
            if design_task_id in (None, "") or tr_id in (None, ""):
                skipped += 1
                continue

            requirements = build_requirements(tr)
            context = {
                "design_task_id": str(design_task_id),
                "tr_id": tr_id,
                "tr_no": tr.get("tr_no") or "",
                "tr_name": tr.get("tr_name") or tr.get("name") or "",
                "pbi": str(pbi),
                "project_id": str(project_id),
                "card_key_prefix": f"TR_{tr_id}",
                "requirements": requirements,
            }
            context_dir = args.output_root / str(design_task_id) / f"TR_{tr_id}"
            context_dir.mkdir(parents=True, exist_ok=True)
            write_json(context_dir / "tr_info.json", context)
            tr_generated += 1

            cida_target = context_dir / "cida_info.json"
            if not requirements:
                remove_cida_info(cida_target)
                missing_requirement += 1
                continue
            if len(requirements) > 1:
                multiple_requirement += 1

            requirement = requirements[0]
            if not requirement.get("requirement_id"):
                remove_cida_info(cida_target)
                missing_requirement_id += 1
                continue
            cida_info = {
                "requirement_number": requirement["requirement_number"],
                "requirement_id": requirement["requirement_id"],
                "project_id": str(project_id),
                "reqType": "cloudalm",
            }
            write_json(cida_target, cida_info)
            cida_generated += 1

    print(
        f"TR contexts generated: {tr_generated}; CIDA contexts generated: {cida_generated}; "
        f"missing direct requirement: {missing_requirement}; "
        f"multi-requirement TRs: {multiple_requirement}; "
        f"missing requirement_id: {missing_requirement_id}; skipped invalid entries: {skipped}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
