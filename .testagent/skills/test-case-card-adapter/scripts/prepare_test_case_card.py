# -*- coding: utf-8 -*-
import argparse
import json
import os
import re


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def normalize_ts_id(ts_id):
    if not ts_id:
        return ""

    text = str(ts_id).strip().lower()

    match = re.match(r"^ts[_-]?(\d+)$", text)
    if match:
        return f"ts_{int(match.group(1)):02d}"

    match = re.match(r"^(\d+)$", text)
    if match:
        return f"ts_{int(match.group(1)):02d}"

    return text


def infer_ts_id_from_tc_json(tc_json):
    base = os.path.basename(tc_json)
    match = re.match(r"^(ts_\d+)_tc\.json$", base, re.IGNORECASE)
    if not match:
        raise ValueError(
            f"无法从文件名推断 ts-id，文件名必须类似 ts_01_tc.json: {tc_json}"
        )
    return match.group(1).lower()


def build_test_case_json(tc_file):
    raw = load_json(tc_file)

    tr_name = raw.get("tr_name", "")
    ts_name = raw.get("ts_name", "")
    ts_type = raw.get("ts_type", "")
    tcs = raw.get("tcs", [])

    tp_map = {}

    for tc in tcs:
        tp_id = tc.get("tp_id_temp", "") or "TP.UNKNOWN"

        if tp_id not in tp_map:
            tp_map[tp_id] = {
                "name": tp_id,
                "number": tp_id,
                "type": ts_type,
                "description": "",
                "requirement_source": ts_name,
                "test_case_list": []
            }

        tp_map[tp_id]["test_case_list"].append({
            "name": tc.get("name", ""),
            "priority": str(tc.get("rank", "")),
            "number": tc.get("case_id", "") or tc.get("tc_id_temp", ""),
            "type": ts_type,
            "pre": tc.get("preparation", ""),
            "test_step": tc.get("test_step", ""),
            "expect_output": tc.get("expect_output", "")
        })

    test_point_list = list(tp_map.values())

    return {
        "title": f"{tr_name}-{ts_name}" if ts_name else tr_name,
        "saved_file_path": "",
        "test_case_count": sum(len(tp["test_case_list"]) for tp in test_point_list),
        "test_point_count": len(test_point_list),
        "test_point_list": test_point_list
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="扩展包根目录")
    parser.add_argument("--ir-id", required=True, help="需求编号，例如 IR20251206000098")
    parser.add_argument("--ts-id", required=False, help="TS编号，例如 ts_01；不传时从 --tc-json 文件名推断")
    parser.add_argument("--tc-json", required=True, help="当前TS测试用例JSON，例如 .design_output/<IR>/test_design/ts_01_tc.json")
    parser.add_argument("--spec-file", required=False, help="兼容保留参数，本脚本不读取测试规格文件")
    parser.add_argument("--card-id-file", required=False, help="当前TS已初始化的card_id文件，用于调用链校验")
    parser.add_argument("--output", required=False, help="输出test_case.json路径；不传时默认 .design_output/<IR>/<ts-id>_test_case.json")
    args = parser.parse_args()

    root_dir = os.path.abspath(args.root)
    output_dir = os.path.join(root_dir, ".design_output", args.ir_id)

    tc_json = os.path.abspath(args.tc_json)
    if not os.path.exists(tc_json):
        raise FileNotFoundError(f"当前TS测试用例JSON不存在: {tc_json}")

    ts_id = normalize_ts_id(args.ts_id) if args.ts_id else infer_ts_id_from_tc_json(tc_json)

    expected_name = f"{ts_id}_tc.json"
    actual_name = os.path.basename(tc_json).lower()
    if actual_name != expected_name.lower():
        raise ValueError(
            f"--ts-id 与 --tc-json 文件名不匹配: ts-id={ts_id}, tc-json={tc_json}"
        )

    if args.spec_file:
        spec_file = os.path.abspath(args.spec_file)
        if not os.path.exists(spec_file):
            raise FileNotFoundError(f"测试规格文件不存在: {spec_file}")

    if args.card_id_file:
        card_id_file = os.path.abspath(args.card_id_file)
        if not os.path.exists(card_id_file):
            raise FileNotFoundError(f"当前TS card_id文件不存在: {card_id_file}")

    if args.output:
        out_file = os.path.abspath(args.output)
    else:
        out_file = os.path.join(output_dir, f"{ts_id}_test_case.json")

    data = build_test_case_json(tc_json)
    save_json(out_file, data)

    print(f"[OK] 生成: {out_file}")
    print(f"[INFO] IR: {args.ir_id}")
    print(f"[INFO] TS: {ts_id}")
    print(f"[INFO] TC JSON: {tc_json}")
    if args.card_id_file:
        print(f"[INFO] CARD ID: {os.path.abspath(args.card_id_file)}")
    print("[DONE] 单TS test-case-card 输入准备完成")


if __name__ == "__main__":
    main()
