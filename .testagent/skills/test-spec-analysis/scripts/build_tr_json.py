#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从测试规格 Markdown 组装“已有 TR”模式的 TR/TS JSON。"""

import argparse
import json
import re
import sys
from pathlib import Path

ANCHOR = "## 平台写入数据"
TS_TYPES = {"scene", "function", "feature", "constraint"}
TR_MD_FIELDS = ["tr_name", "description", "resolve_description", "requirement_ids",
                "function_numbers", "feature_numbers"]


def fail(message: str) -> None:
    raise ValueError(message)


def read_section(md_text: str) -> list[str]:
    lines = md_text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.strip() == ANCHOR]
    if len(starts) != 1:
        fail(f"必须且只能存在一个锚点 '{ANCHOR}'，实际为 {len(starts)} 个。")
    start = starts[0]
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start:end]


def parse_table(section_lines: list[str], sub_header: str) -> list[list[str]]:
    try:
        start = next(i for i, line in enumerate(section_lines) if line.strip() == f"### {sub_header}")
    except StopIteration:
        fail(f"平台写入数据章节缺少 '### {sub_header}' 子节。")
    rows, started = [], False
    for line in section_lines[start + 1:]:
        stripped = line.strip()
        if stripped.startswith("##") or stripped.startswith("###"):
            break
        if stripped.startswith("|"):
            started = True
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if any(cells) and all(re.fullmatch(r":?-{2,}:?", cell) for cell in cells if cell):
                continue
            rows.append(cells)
        elif started:
            break
    return rows


def parse_tr(section_lines: list[str]) -> dict:
    values = {}
    for cells in parse_table(section_lines, "TR"):
        if len(cells) >= 2 and cells[0] != "字段":
            value = cells[1]
            if value.startswith("<") and value.endswith(">"):
                value = ""
            values[cells[0]] = value
    missing = [field for field in TR_MD_FIELDS if field not in values]
    if missing:
        fail("TR 表缺少字段: " + "，".join(missing))
    return values


def split_ids(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        parts = value
    else:
        parts = re.split(r"[,，]", str(value))
    result = []
    for item in parts:
        item = str(item).strip()
        if item and item not in result:
            result.append(item)
    return result


def required_ids(tr_info: dict) -> list[str]:
    ids = []
    for requirement in tr_info.get("requirements") or []:
        number = str(requirement.get("requirement_number") or "").strip()
        if not number:
            fail("tr_info.json 的 requirements[] 存在缺少 requirement_number 的条目。")
        if number not in ids:
            ids.append(number)
    if not ids:
        fail("tr_info.json 的 requirements[] 为空，无法生成测试规格 JSON。")
    return ids


def parse_ts(section_lines: list[str], allowed: set[str]) -> list[dict]:
    specs = []
    for cells in parse_table(section_lines, "TS 清单"):
        if len(cells) < 5:
            continue
        name, ts_type, req_value, description, resolve = cells[:5]
        if name in {"", "ts_name"} or (name.startswith("<") and name.endswith(">")):
            continue
        if ts_type not in TS_TYPES:
            fail(f"TS「{name}」的 ts_type「{ts_type}」不在 {sorted(TS_TYPES)} 内。")
        ids = split_ids(req_value)
        unknown = [item for item in ids if item not in allowed]
        if unknown:
            fail(f"TS「{name}」引用了非当前 TR 需求: {','.join(unknown)}")
        specs.append({
            "ts_name": name,
            "ts_type": ts_type,
            "requirement_ids": ",".join(ids),
            "description": description,
            "resolve_description": resolve,
        })
    if not specs:
        fail("TS 清单为空或仍为占位内容。")
    return specs


def normalize_relation(value) -> str:
    return ",".join(split_ids(value))


def main() -> None:
    parser = argparse.ArgumentParser(description="从测试规格 md 生成已有 TR 模式 JSON")
    parser.add_argument("md", help="包含‘平台写入数据’章节的测试规格 Markdown")
    parser.add_argument("--tr-info", required=True, help="当前 TR 的 tr_info.json")
    parser.add_argument("--out", default=None, help="输出路径，默认与 md 同目录的 tr_ts.json")
    args = parser.parse_args()

    try:
        md_path = Path(args.md)
        tr_info_path = Path(args.tr_info)
        if not md_path.is_file():
            fail(f"Markdown 不存在: {md_path}")
        if not tr_info_path.is_file():
            fail(f"tr_info.json 不存在: {tr_info_path}")

        tr_info = json.loads(tr_info_path.read_text(encoding="utf-8-sig"))
        expected_ids = required_ids(tr_info)
        section = read_section(md_path.read_text(encoding="utf-8-sig"))
        md_tr = parse_tr(section)
        md_ids = split_ids(md_tr["requirement_ids"])
        if set(md_ids) != set(expected_ids) or len(md_ids) != len(expected_ids):
            fail("Markdown TR requirement_ids 与 tr_info.json.requirements[] 不一致："
                 f"Markdown={md_ids}，tr_info={expected_ids}")

        test_specs = parse_ts(section, set(expected_ids))
        tr = {
            "design_task_id": str(tr_info.get("design_task_id") or ""),
            "tr_id": tr_info.get("tr_id"),
            "tr_no": tr_info.get("tr_no") or "",
            "tr_name": tr_info.get("tr_name") or "",
            "description": tr_info.get("description") or "",
            "resolve_description": tr_info.get("resolve_description") or "",
            "creator": tr_info.get("creator") or "",
            "requirement_ids": ",".join(expected_ids),
            "function_numbers": normalize_relation(tr_info.get("relation_function")),
            "feature_numbers": normalize_relation(tr_info.get("relation_feature")),
        }
        required = ["design_task_id", "tr_id", "tr_name"]
        missing = [key for key in required if tr[key] in {"", None}]
        if missing:
            fail("tr_info.json 缺少已有 TR 必需字段: " + "，".join(missing))

        # Markdown 的 TR 元数据必须来自 tr_info；发现漂移即失败。
        for field in ("tr_name", "description", "resolve_description"):
            if md_tr[field] != tr[field]:
                fail(f"Markdown TR 字段 {field} 与 tr_info.json 不一致。")

        result = {
            "_meta": {
                "tr_mode": "existing",
                "source": "coretest-explore / build_tr_json.py",
                "extracted_from": md_path.name,
                "ts_count": len(test_specs),
            },
            "tr": tr,
            "test_specs": test_specs,
        }
        out_path = Path(args.out) if args.out else md_path.parent / "tr_ts.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已生成已有 TR JSON：{len(test_specs)} 条 TS -> {out_path}")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        sys.exit(f"错误：{exc}")


if __name__ == "__main__":
    main()
