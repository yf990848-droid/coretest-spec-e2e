#!/usr/bin/env python3
"""Generate idempotent TR-level cida_info.json files from init MCP output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate TR-level init contexts")
    parser.add_argument("--design-task-info", required=True, type=Path)
    parser.add_argument("--output-root", default=Path(".design_output"), type=Path)
    return parser.parse_args()


def requirement_number(item: dict[str, Any]) -> str:
    return str(item.get("requirement_id") or item.get("requirement_number") or "").strip()


def build_requirements(items: Any) -> list[dict[str, Any]]:
    requirements: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        number = requirement_number(item)
        if not number or number in seen:
            continue
        seen.add(number)
        requirement: dict[str, Any] = {
            "requirement_number": number,
            "requirement_type": item.get("requirement_type") or ("SR" if number.startswith("SR") else "IR"),
            "reqType": "cloudalm",
        }
        alm_id = item.get("requirementAlmId") or item.get("requirement_alm_id")
        if alm_id not in (None, ""):
            requirement["requirement_id"] = str(alm_id)
        requirements.append(requirement)
    return requirements


def main() -> int:
    args = parse_args()
    with args.design_task_info.open("r", encoding="utf-8") as source:
        init_result = json.load(source)

    pbi = init_result.get("pbi")
    project_id = init_result.get("project_id")
    tasks = init_result.get("data")
    if pbi in (None, "") or project_id in (None, "") or not isinstance(tasks, list):
        raise ValueError("design_task_info.json must contain pbi, project_id and data[]")

    generated = 0
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

            context = {
                "design_task_id": str(design_task_id),
                "tr_id": tr_id,
                "tr_no": tr.get("tr_no") or "",
                "tr_name": tr.get("tr_name") or tr.get("name") or "",
                "pbi": str(pbi),
                "project_id": str(project_id),
                "card_key_prefix": f"TR_{tr_id}",
                "requirements": build_requirements(tr.get("ir_list")),
            }
            context_dir = args.output_root / str(design_task_id) / f"TR_{tr_id}"
            context_dir.mkdir(parents=True, exist_ok=True)
            target = context_dir / "cida_info.json"
            with target.open("w", encoding="utf-8", newline="\n") as output:
                json.dump(context, output, ensure_ascii=False, indent=2)
                output.write("\n")
            generated += 1

    print(f"TR contexts generated: {generated}; skipped invalid entries: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
