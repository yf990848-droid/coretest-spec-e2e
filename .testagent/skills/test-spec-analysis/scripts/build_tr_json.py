#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_tr_json.py —— 从测试规格 md 后段提取，组装平台 TR/TS JSON

职责：只读测试规格 md 的「## 平台写入数据」固定章节，提取 TR 段与 TS 清单，
补 design_task_id（命令参数）与 creator（环境变量 USERNAME），套死 JSON 形状落盘。
不读 rules、不读 _index、不做内容校验——内容由 md 决定（其规则来自 rules），
脚本只保证 JSON 形状合规（字段齐、可传 create-tr MCP）。

用法：
    python build_tr_json.py <测试规格.md> --design-task-id 281
    （creator 取自环境变量 USERNAME；输出默认落 md 同目录 tr_ts.json）
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

ANCHOR = "## 平台写入数据"
PENDING = "<PENDING-coretest-init>"
TS_TYPES = {"scene", "function", "feature", "constraint"}
# TR 段中由模型写入 md 的业务字段
TR_MD_FIELDS = ["tr_name", "description", "resolve_description",
                "requirement_ids", "function_numbers", "feature_numbers"]
# 固定质量属性 TS：每个 TR 自动补齐这 9 类（平台固定要求，零判断）。
# ts_name = description = resolve_description = <tr_name>_<中文测试类型>；
# requirement_ids 留空；ts_type 取对应英文枚举。
# 注意：这 9 类 ts_type 不在 TS_TYPES（四类）内——它们由脚本生成、不过 parse_ts 校验，故不受四类约束。
QUALITY_TS = [
    ("性能测试", "performance"),
    ("可靠性测试", "reliability"),
    ("易用性测试", "usability"),
    ("安全测试", "security"),
    ("可服务性测试", "serviceability"),
    ("功能安全测试", "funcSafety"),
    ("兼容性测试", "compatibility"),
    ("可测试性测试", "testability"),
    ("客户化测试", "customized"),
]


def read_section(md_text: str) -> list[str]:
    """截取「## 平台写入数据」到下一个同级 ## 标题（或文件尾）之间的行。"""
    lines = md_text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == ANCHOR:
            start = i
            break
    if start is None:
        sys.exit(f"错误：未找到锚点 '{ANCHOR}'，md 缺少平台写入数据章节。")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return lines[start:end]


def parse_table(section_lines: list[str], sub_header: str) -> list[list[str]]:
    """定位 ### <sub_header> 子节，解析其下第一个 markdown 表格，返回数据行（含表头行）。"""
    sub_idx = None
    for i, line in enumerate(section_lines):
        if line.strip() == f"### {sub_header}":
            sub_idx = i
            break
    if sub_idx is None:
        sys.exit(f"错误：平台写入数据章节缺少 '### {sub_header}' 子节。")

    rows = []
    started = False
    for line in section_lines[sub_idx + 1:]:
        s = line.strip()
        if s.startswith("##") or s.startswith("###"):
            break
        if s.startswith("|"):
            started = True
            cells = [c.strip() for c in s.strip("|").split("|")]
            # 跳过分隔行 |---|---|
            if any(cells) and all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                continue
            rows.append(cells)
        elif started:
            break  # 表格结束
    return rows


def parse_tr(section_lines: list[str]) -> dict:
    rows = parse_table(section_lines, "TR")
    kv = {}
    for cells in rows:
        if len(cells) < 2:
            continue
        key, val = cells[0], cells[1]
        if key == "字段":  # 表头
            continue
        # 未替换的模板占位（<...>）视为未填
        if val.startswith("<") and val.endswith(">"):
            val = ""
        kv[key] = val
    missing = []
    for f in TR_MD_FIELDS:
        if f not in kv:
            missing.append(f)
        elif kv[f] == "" and f not in ("function_numbers", "feature_numbers"):  # 编号字段允许为空
            missing.append(f + "(未填)")
    if missing:
        sys.exit("错误：TR 表以下字段未填：" + "，".join(missing)
                 + "。请检查 md「平台写入数据」的 TR 表是否已替换占位并填入真实值。")
    return kv


def parse_ts(section_lines: list[str]) -> list[dict]:
    rows = parse_table(section_lines, "TS 清单")
    specs = []
    for cells in rows:
        if len(cells) < 5:
            continue
        ts_name, ts_type, req_ids, desc, resolve = cells[0], cells[1], cells[2], cells[3], cells[4]
        if ts_name in ("ts_name", ""):  # 表头或空行
            continue
        if ts_name.startswith("<") and ts_name.endswith(">"):  # 未替换占位行
            continue
        # 卡 ts_type：必须是四类之一，否则报错（封闭枚举，错了平台才拒太被动）
        if ts_type not in TS_TYPES:
            sys.exit(f"错误：TS「{ts_name}」的 ts_type 为「{ts_type}」，"
                     f"不在四类 {sorted(TS_TYPES)} 内。请检查 md TS 清单的 ts_type 列。")
        specs.append({
            "ts_name": ts_name,
            "ts_type": ts_type,
            "requirement_ids": req_ids,
            "description": desc,
            "resolve_description": resolve,
        })
    if not specs:
        sys.exit("错误：TS 清单为空。请检查 md「平台写入数据」的 TS 表是否已填真实 TS、"
                 "是否还停留在占位行。")
    return specs

def build_quality_specs(tr_name: str) -> list[dict]:
    """按固定规则为该 TR 生成 9 条质量属性 TS（与平台对齐）。"""
    specs = []
    for cn_name, ts_type in QUALITY_TS:
        label = f"{tr_name}_{cn_name}"
        specs.append({
            "ts_name": label,
            "ts_type": ts_type,
            "requirement_ids": "",
            "description": label,
            "resolve_description": label,
        })
    return specs

def main():
    ap = argparse.ArgumentParser(description="从测试规格 md 提取组装平台 TR/TS JSON")
    ap.add_argument("md", help="测试规格 md 路径（含「## 平台写入数据」章节）")
    ap.add_argument("--design-task-id", required=True,
                    help="必填，设计任务ID（沙盒用281），来自 CloudSpider 页面 dtId")
    ap.add_argument("--out", default=None,
                    help="可选，JSON 输出路径；默认 md 同目录 tr_ts.json")
    args = ap.parse_args()

    creator = os.getenv("USERNAME")
    if not creator:
        sys.exit("错误：环境变量 USERNAME 为空，无法确定 creator（避免把空值写平台）。")

    md_path = Path(args.md)
    if not md_path.exists():
        sys.exit(f"错误：md 文件不存在：{md_path}")
    md_text = md_path.read_text(encoding="utf-8-sig")

    section = read_section(md_text)
    tr_kv = parse_tr(section)
    test_specs = parse_ts(section)
    test_specs.extend(build_quality_specs(tr_kv["tr_name"]))

    # 套死 JSON 形状：tr 段字段顺序固定，含 create-tr 全部 7 参数 + feature_numbers
    tr = {
        "design_task_id": args.design_task_id,
        "tr_name": tr_kv["tr_name"],
        "description": tr_kv["description"],
        "resolve_description": tr_kv["resolve_description"],
        "creator": creator,
        "requirement_ids": tr_kv["requirement_ids"],
        "function_numbers": tr_kv["function_numbers"] or PENDING,
        "feature_numbers": tr_kv.get("feature_numbers", ""),
    }

    result = {
        "_meta": {
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

    print(f"已生成 JSON：{len(test_specs)} 条 TS -> {out_path}")


if __name__ == "__main__":
    main()
