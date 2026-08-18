#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_tp_tc_json.py —— 从测试设计 md 后段提取，组装 TP/TC 的 MCP 入参 JSON

职责：只读 ts_<NN>_test_design.md / ts_<NN>_test_cases.md 的
「## 平台写入数据 - TP」/「## 平台写入数据 - TC」固定章节，提取表格，
补 designTaskId（命令参数）与 creator（环境变量 USERNAME），套死 JSON 形状落盘。
不读 rules、不做内容校验、不调用 MCP——内容由 md 决定（其格式规则来自
../../rules/tp-tc-output.md），脚本只保证 JSON 形状合规。

<PENDING> 占位字段（tsId/parentTrId/tp_id/tr_id 等）原样写入 json，不报错、
不阻断——这些字段预期要等后续步骤（人工核实平台 id、调用 create_tp 拿到真实
tp_id 后回填）才能补齐。脚本结束时打印汇总，列出每个 TS 还剩多少 PENDING 字段。

用法：
    python build_tp_tc_json.py <test_design目录> --design-task-id 281
    （处理 .design_output/<IR>/test_design/ 下全部 TS）

    python build_tp_tc_json.py <test_design目录> --design-task-id 281 --ts 01
    （仅处理指定 test_design 目录下序号 01 的 TS）

    creator 取自环境变量 USERNAME；输入目录为：
    .design_output/<IR>/test_design/

输出落同一目录：
    ts_<NN>_tp.json / ts_<NN>_tc.json
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

TP_ANCHOR = "## 平台写入数据 - TP"
TC_ANCHOR = "## 平台写入数据 - TC"
PENDING = "<PENDING>"

# TP 表列名，顺序必须与 ../../rules/tp-tc-output.md 中定义的表头一致
TP_COLUMNS = [
    "tp_id_temp", "tpName", "description", "resolveDescription", "rank",
    "tsId", "parentTrId", "tpType", "tpSourceType", "requirement_ids",
    "dimension", "raw_factors",
]
# TC 表列名，同上
TC_COLUMNS = [
    "tc_id_temp", "tp_id_temp", "name", "rank",
    "preparation", "test_step", "expect_output", "case_id",
    "TestType", "AutoType", "envtype", "DesignNote",
]

DIMENSIONS = {"基于业务场景", "基于业务内部实现", "功能交互设计", "测试类型交互设计"}

# 调用 create_tp/create_tc 时才能补齐的平台真实 id 字段，转 json 时统一加上完整占位串
TP_RUNTIME_PENDING = {
    "tsId": "<TODO:tsId>",
    "parentTrId": "<TODO:parentTrId>",
}
TC_RUNTIME_PENDING = {
    "tp_id": "<TODO:tp_id_after_create_tp>",
    "tr_id": "<TODO:tr_id>",
}

TS_FILENAME_RE = re.compile(r"^ts_(\d{2})_test_design\.md$")


def find_ts_pairs(test_design_dir: Path) -> list[tuple[str, Path, Path]]:
    """扫描 test_design/ 目录，返回 [(NN, design_md_path, cases_md_path), ...]，按 NN 排序。"""
    pairs = []
    for f in sorted(test_design_dir.glob("ts_*_test_design.md")):
        m = TS_FILENAME_RE.match(f.name)
        if not m:
            continue
        nn = m.group(1)
        cases_path = test_design_dir / f"ts_{nn}_test_cases.md"
        if not cases_path.exists():
            print(f"警告：TS {nn} 缺少 ts_{nn}_test_cases.md，跳过该 TS", file=sys.stderr)
            continue
        pairs.append((nn, f, cases_path))
    return pairs


def read_section(md_text: str, anchor: str, source_name: str) -> list[str]:
    """截取 anchor 标题到下一个同级 ## 标题（或文件尾）之间的行。"""
    lines = md_text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == anchor:
            start = i
            break
    if start is None:
        sys.exit(f"错误：{source_name} 未找到锚点 '{anchor}'，md 缺少固定表格区。")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return lines[start:end]


def parse_first_table(section_lines: list[str], source_name: str, anchor: str) -> list[list[str]]:
    """解析 anchor 章节下第一个 markdown 表格，返回数据行（不含表头、不含分隔行）。"""
    rows = []
    header_skipped = False
    started = False
    for line in section_lines:
        s = line.strip()
        if not s.startswith("|"):
            if started:
                break
            continue
        started = True
        cells = [c.strip() for c in s.strip("|").split("|")]
        # 跳过分隔行 |---|---|
        if any(cells) and all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if not header_skipped:
            header_skipped = True
            continue  # 第一行是表头，跳过
        rows.append(cells)
    if not rows:
        sys.exit(f"错误：{source_name} 的 '{anchor}' 章节下未找到有效表格数据行。")
    return rows


def unescape_cell(value: str) -> str:
    """还原表格单元格内的换行转义：<br> -> \\n"""
    return value.replace("<br>", "\n")


def row_to_dict(cells: list[str], columns: list[str], source_name: str) -> dict:
    if len(cells) != len(columns):
        sys.exit(
            f"错误：{source_name} 表格列数 {len(cells)} 与预期 {len(columns)} 不符，"
            f"预期列：{columns}。请检查 md 表格是否被手动改动过格式。"
        )
    return dict(zip(columns, cells))


def parse_tp_table(section_lines: list[str], source_name: str) -> list[dict]:
    rows = parse_first_table(section_lines, source_name, TP_ANCHOR)
    tps = []
    for cells in rows:
        d = row_to_dict(cells, TP_COLUMNS, source_name)
        if d["tp_id_temp"] in ("", "tp_id_temp"):
            continue  # 跳过空行/误读的表头
        if d["dimension"] not in DIMENSIONS and d["dimension"] != PENDING:
            sys.exit(
                f"错误：{source_name} 中 TP「{d['tp_id_temp']}」的 dimension 为"
                f"「{d['dimension']}」，不在四类 {sorted(DIMENSIONS)} 内。"
            )
        d["description"] = unescape_cell(d["description"])
        d["raw_factors"] = [f.strip() for f in d["raw_factors"].split(",") if f.strip()] \
            if d["raw_factors"] and d["raw_factors"] != PENDING else []
        tps.append(d)
    if not tps:
        sys.exit(f"错误：{source_name} 的 TP 表为空。请检查是否还停留在占位/示例行。")
    return tps


def parse_tc_table(section_lines: list[str], source_name: str) -> list[dict]:
    rows = parse_first_table(section_lines, source_name, TC_ANCHOR)
    tcs = []
    for cells in rows:
        d = row_to_dict(cells, TC_COLUMNS, source_name)
        if d["tc_id_temp"] in ("", "tc_id_temp"):
            continue
        d["TestType"] = d["TestType"].strip() or "1"
        d["AutoType"] = d["AutoType"].strip() or "0"
        if not d["DesignNote"].strip():
            sys.exit(
                f"错误：{source_name} 中 TC「{d['tc_id_temp']}」的 DesignNote 不能为空。"
            )
        for field in ("preparation", "test_step", "expect_output", "DesignNote"):
            d[field] = unescape_cell(d[field])
        tcs.append(d)
    if not tcs:
        sys.exit(f"错误：{source_name} 的 TC 表为空。请检查是否还停留在占位/示例行。")
    return tcs


def count_pending(records: list[dict], pending_fields: list[str]) -> int:
    n = 0
    for r in records:
        for f in pending_fields:
            if r.get(f) == PENDING:
                n += 1
    return n


def build_tp_json(tr_name: str, ts_name: str, ts_type: str, tps: list[dict],
                  design_task_id: str, creator: str) -> dict:
    out_tps = []
    for d in tps:
        item = {
            "tp_id_temp": d["tp_id_temp"],
            "tpName": d["tpName"],
            "description": d["description"],
            "resolveDescription": d["resolveDescription"],
            "rank": d["rank"],
            "designTaskId": design_task_id,
            "creator": creator,
            "tsId": TP_RUNTIME_PENDING["tsId"] if d["tsId"] == PENDING else d["tsId"],
            "parentTrId": TP_RUNTIME_PENDING["parentTrId"] if d["parentTrId"] == PENDING else d["parentTrId"],
            "tpType": d["tpType"],
            "tpSourceType": d["tpSourceType"],
            "requirement_ids": d["requirement_ids"],
            "_dimension": d["dimension"],
            "_raw_factors": d["raw_factors"],
        }
        out_tps.append(item)
    return {"tr_name": tr_name, "ts_name": ts_name, "ts_type": ts_type, "tps": out_tps}


def build_tc_json(tr_name: str, ts_name: str, ts_type: str, tcs: list[dict], creator: str) -> dict:
    out_tcs = []
    for d in tcs:
        case_id = d["case_id"]
        # case_id_prefix/start_value/number 由脚本派生，不依赖 md
        case_id_prefix = case_id.rsplit("_", 2)[0] if case_id.count("_") >= 2 else case_id
        item = {
            "tc_id_temp": d["tc_id_temp"],
            "tp_id_temp": d["tp_id_temp"],
            "name": d["name"],
            "rank": d["rank"],
            "preparation": d["preparation"],
            "test_step": d["test_step"],
            "expect_output": d["expect_output"],
            "case_id": case_id,
            "TestType": d["TestType"],
            "AutoType": d["AutoType"],
            "envtype": d["envtype"].strip(),
            "DesignNote": d["DesignNote"],
            "case_id_prefix": case_id_prefix,
            "case_id_start_value": 0,
            "case_id_number": "1",
            "auto_type": 0,
            "creator": creator,
            "owner": "",
            "tp_id": TC_RUNTIME_PENDING["tp_id"],
            "tr_id": TC_RUNTIME_PENDING["tr_id"],
        }
        out_tcs.append(item)
    return {"tr_name": tr_name, "ts_name": ts_name, "ts_type": ts_type, "tcs": out_tcs}


META_ANCHOR = "## 平台写入数据 - 元信息"
META_FIELDS = ("tr_name", "ts_name", "ts_type")


def extract_ts_meta(design_md_text: str, source_name: str) -> dict:
    """从 design md 末尾固定表格区的「## 平台写入数据 - 元信息」小表读取
    tr_name/ts_name/ts_type。小表为两列（字段|值），按行名取。

    入固定表格区而非从前段叙述标签抓：前段标签写法不稳定（曾出现
    所属TR / TR名称 等多种写法导致抓空），固定表格区按行名确定读取，
    不受 md 叙述措辞影响。
    """
    section = read_section(design_md_text, META_ANCHOR, source_name)
    rows = parse_first_table(section, source_name, META_ANCHOR)
    meta = {}
    for cells in rows:
        if len(cells) < 2:
            continue
        key, val = cells[0].strip(), cells[1].strip()
        if key in META_FIELDS:
            meta[key] = val
    missing = [f for f in META_FIELDS if not meta.get(f)]
    if missing:
        sys.exit(
            f"错误：{source_name} 的「{META_ANCHOR}」小表缺少字段或值为空：{missing}。"
            f"请确认 design md 末尾元信息小表完整（tr_name/ts_name/ts_type 三行均有值）。"
        )
    return meta


def process_pair(nn: str, design_path: Path, cases_path: Path,
                 design_task_id: str, creator: str) -> tuple[dict, dict, dict]:
    design_text = design_path.read_text(encoding="utf-8-sig")
    cases_text = cases_path.read_text(encoding="utf-8-sig")

    meta = extract_ts_meta(design_text, design_path.name)
    tr_name, ts_name, ts_type = meta["tr_name"], meta["ts_name"], meta["ts_type"]

    tp_section = read_section(design_text, TP_ANCHOR, design_path.name)
    tps = parse_tp_table(tp_section, design_path.name)

    tc_section = read_section(cases_text, TC_ANCHOR, cases_path.name)
    tcs = parse_tc_table(tc_section, cases_path.name)

    tp_json = build_tp_json(tr_name, ts_name, ts_type, tps, design_task_id, creator)
    tc_json = build_tc_json(tr_name, ts_name, ts_type, tcs, creator)

    pending_summary = {
        "ts": f"ts_{nn}",
        "ts_name": ts_name,
        "tp_count": len(tps),
        "tc_count": len(tcs),
        "tp_pending_fields": count_pending(tps, ["tsId", "parentTrId"]),
    }
    return tp_json, tc_json, pending_summary


def main():
    ap = argparse.ArgumentParser(description="从测试设计 md 提取组装 TP/TC 的 MCP 入参 JSON")
    ap.add_argument("test_design_dir", help="test_design目录路径（如 .design_output/<IR>/test_design/）")
    ap.add_argument("--design-task-id", required=True,
                    help="必填，设计任务ID（沙盒用281），来自 CloudSpider 页面 dtId")
    ap.add_argument("--ts", default=None,
                    help="可选，仅处理指定 TS 序号（如 01）；不传则处理全部 TS")
    args = ap.parse_args()

    creator = os.getenv("USERNAME")
    if not creator:
        sys.exit("错误：环境变量 USERNAME 为空，无法确定 creator（避免把空值写入 json）。")

    test_design_dir = Path(args.test_design_dir)
    if not test_design_dir.exists():
        sys.exit(f"错误：目录不存在：{test_design_dir}")

    pairs = find_ts_pairs(test_design_dir)
    if not pairs:
        sys.exit(f"错误：{test_design_dir} 下未找到任何 ts_<NN>_test_design.md / ts_<NN>_test_cases.md 配对。")

    if args.ts:
        target_nn = args.ts.replace("TS.", "").replace("TS", "").strip().zfill(2)
        pairs = [p for p in pairs if p[0] == target_nn]
        if not pairs:
            sys.exit(f"错误：未找到序号 {args.ts} 对应的 md 文件配对，请检查 TS 序号。")

    summaries = []
    for nn, design_path, cases_path in pairs:
        tp_json, tc_json, summary = process_pair(
            nn, design_path, cases_path, args.design_task_id, creator
        )

        tp_out = test_design_dir / f"ts_{nn}_tp.json"
        tc_out = test_design_dir / f"ts_{nn}_tc.json"
        tp_out.write_text(json.dumps(tp_json, ensure_ascii=False, indent=2), encoding="utf-8")
        tc_out.write_text(json.dumps(tc_json, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"ts_{nn}({summary['ts_name']}): {summary['tp_count']} 个 TP -> {tp_out.name}, "
              f"{summary['tc_count']} 个 TC -> {tc_out.name}")
        summaries.append(summary)

    print()
    print("=== PENDING 字段汇总（需后续步骤补齐）===")
    any_pending = False
    for s in summaries:
        if s["tp_pending_fields"] > 0:
            any_pending = True
            print(f"  {s['ts']}: {s['tp_pending_fields']} 处 TP 字段待补（tsId/parentTrId）")
    print("  所有 TC 均有 2 处固定待补字段（tp_id/tr_id），需等 create_tp 调用成功后回填")
    if not any_pending:
        print("  （TP 表中未发现 <PENDING> 字段）")


if __name__ == "__main__":
    main()
