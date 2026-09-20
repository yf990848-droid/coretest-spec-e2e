#!/usr/bin/env python3
"""Validate the per-TS factor plan without changing TP/TC Markdown or JSON."""

import argparse
import json
import re
from pathlib import Path


def read_json(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        return json.load(stream)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(plan, tp_json, ts_key, ts_type, max_ts=None, max_tp=None):
    require(isinstance(plan, dict) and isinstance(tp_json, dict), "因子计划和 TP JSON 必须是对象")
    limits = plan.get("limits", {"max_ts_factors": 5, "max_tp_factors": 3})
    require(isinstance(limits, dict), "因子数量上限格式错误")
    max_ts = max_ts if max_ts is not None else limits.get("max_ts_factors")
    max_tp = max_tp if max_tp is not None else limits.get("max_tp_factors")
    require(type(max_ts) is int and max_ts > 0 and type(max_tp) is int and max_tp > 0,
            "因子数量上限必须为正整数")
    require(plan.get("ts_key") == ts_key, "因子计划 ts_key 与当前 TS 不一致")
    require(plan.get("ts_type") == ts_type, "因子计划 ts_type 与 catalog 不一致")
    tests = plan.get("test_factors")
    scenes = plan.get("scene_factors")
    selections = plan.get("tp_factors")
    require(isinstance(tests, list) and isinstance(scenes, list) and isinstance(selections, dict),
            "test_factors、scene_factors、tp_factors 类型错误")
    require(ts_type == "scene" or not scenes, "非 scene TS 不能关联 SceneFactor")
    require(len(tests) + len(scenes) <= max_ts, "TS 因子数量超过上限")
    test_ids, scene_codes = set(), set()
    for factor in tests:
        require(isinstance(factor, dict), "TestFactor 必须是对象")
        factor_id = factor.get("testFactorId")
        require(isinstance(factor_id, str) and re.fullmatch(r"[a-fA-F0-9-]{24,}", factor_id),
                "testFactorId 必须是因子 UUID，不得使用 TS 关系 ID")
        require(factor_id not in test_ids, "重复 TestFactor UUID")
        require(all(factor.get(field) not in (None, "") for field in
                    ("name", "number", "type", "assoActType", "sourceType", "factorType", "pbi")),
                "TestFactor 缺少名称、编码、类型或来源")
        require(factor["sourceType"] == "TestFactorLibrary", "TestFactor 来源类型错误")
        test_ids.add(factor_id)
    for factor in scenes:
        require(isinstance(factor, dict), "SceneFactor 必须是对象")
        code = factor.get("factorCode")
        require(isinstance(code, str) and code and code not in scene_codes,
                "SceneFactor 编码为空或重复")
        require(factor.get("sceneFactorCode") == code, "SceneFactor 两个编码字段不一致")
        require(all(factor.get(field) for field in ("factorName", "assoActType", "sourceType", "pbi")),
                "SceneFactor 缺少名称或关联类型")
        scene_codes.add(code)
    tps = tp_json.get("tps")
    require(isinstance(tps, list) and tps, "TP JSON 缺少 tps[]")
    tp_ids = [tp.get("tp_id_temp") for tp in tps if isinstance(tp, dict)]
    require(len(tp_ids) == len(tps) and all(isinstance(key, str) and key for key in tp_ids)
            and len(set(tp_ids)) == len(tp_ids), "TP 临时 ID 为空或重复")
    require(set(selections) == set(tp_ids), "因子计划必须精确覆盖当前 TS 的全部 TP")
    used_tests, used_scenes = set(), set()
    for tp_id, selected in selections.items():
        require(isinstance(selected, dict), f"{tp_id} 因子选择必须是对象")
        test_selection = selected.get("test_factor_ids")
        scene_selection = selected.get("scene_factor_codes")
        require(isinstance(test_selection, list) and isinstance(scene_selection, list),
                f"{tp_id} 必须明确给出两个因子数组（允许为空）")
        require(len(test_selection) + len(scene_selection) <= max_tp, f"{tp_id} 因子数量超过上限")
        require(len(set(test_selection)) == len(test_selection) and
                len(set(scene_selection)) == len(scene_selection), f"{tp_id} 有重复因子")
        require(set(test_selection) <= test_ids and set(scene_selection) <= scene_codes,
                f"{tp_id} 选择的因子不属于当前 TS")
        used_tests.update(test_selection)
        used_scenes.update(scene_selection)
    require(used_tests == test_ids and used_scenes == scene_codes,
            "未被任何 TP 使用的 TS 因子必须从计划中剔除")
    return {"ts_key": ts_key, "tp_count": len(tps), "test_factors": len(tests),
            "scene_factors": len(scenes)}


def verify_candidates(evidence, plan, tp_json, ts_key, ts_type):
    require(isinstance(evidence, dict) and evidence.get("success") is True,
            "图谱检索未成功，不能判定无匹配因子")
    require(evidence.get("ts_key") == ts_key and evidence.get("ts_type") == ts_type
            and isinstance(evidence.get("product"), str) and evidence["product"].strip(),
            "检索证据与当前 TS 或产品不一致")
    labels = ["TestFactor", "SceneFactor"] if ts_type == "scene" else ["TestFactor"]
    targets = ["ts"] + [tp["tp_id_temp"] for tp in tp_json["tps"]]
    queries = evidence.get("queries")
    require(isinstance(queries, list) and len(queries) == len(targets) * len(labels),
            "TS/TP 的因子查询次数不足")
    require(all(isinstance(row, dict) for row in queries), "图谱查询记录格式错误")
    require([(row.get("target"), row.get("label")) for row in queries]
            == [(target, label) for target in targets for label in labels],
            "图谱查询目标或因子类型不完整")
    for row in queries:
        response = row.get("response")
        require(isinstance(row.get("query"), str) and row["query"].strip()
                and isinstance(response, dict) and response.get("ok") is True
                and isinstance(response.get("data"), list)
                and response.get("count") == len(response["data"]),
                "图谱查询缺少有效成功响应")
    for kind, id_field, plan_id in (("test_factors", "test_factor_id", "testFactorId"),
                                    ("scene_factors", "factor_code", "factorCode")):
        found = evidence.get(kind)
        require(isinstance(found, list), "图谱候选列表缺失")
        identifiers = {item.get(id_field) for item in found if isinstance(item, dict)}
        label = "TestFactor" if kind == "test_factors" else "SceneFactor"
        raw_ids = {item.get(id_field) for row in queries if row["label"] == label
                   for item in row["response"]["data"] if isinstance(item, dict)}
        require(identifiers <= raw_ids, "候选标识不属于图谱原始查询结果")
        require(all(item[plan_id] in identifiers for item in plan[kind]),
                "因子计划包含未在图谱查询中查到的标识")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan-file", required=True)
    parser.add_argument("--tp-file", required=True)
    parser.add_argument("--candidates-file", required=True)
    parser.add_argument("--ts-key", required=True)
    parser.add_argument("--ts-type", required=True)
    parser.add_argument("--max-ts-factors", type=int)
    parser.add_argument("--max-tp-factors", type=int)
    args = parser.parse_args()
    try:
        result = validate(read_json(args.plan_file), read_json(args.tp_file), args.ts_key,
                          args.ts_type, args.max_ts_factors, args.max_tp_factors)
        verify_candidates(read_json(args.candidates_file), read_json(args.plan_file),
                          read_json(args.tp_file), args.ts_key, args.ts_type)
        print(json.dumps({"success": True, **result}, ensure_ascii=False))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(1, json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
