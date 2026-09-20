#!/usr/bin/env python3
"""Query graph factor candidates for one TS and save auditable evidence."""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def read_json(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        return json.load(stream)


def search(graph_script, label, product, query):
    command = [sys.executable, str(graph_script), "search", "--label", label,
               "--product", product, "--query", query, "--top-k", "10"]
    proc = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} 查询未返回合法 JSON: {proc.stderr or proc.stdout}") from exc
    if proc.returncode or not isinstance(result, dict) or result.get("ok") is not True:
        raise ValueError(f"{label} 查询失败: {result.get('error') if isinstance(result, dict) else result}")
    if not isinstance(result.get("data"), list) or result.get("count") != len(result["data"]):
        raise ValueError(f"{label} 查询结果格式错误")
    return result


def build_queries(catalog, tp_json, ts_key, ts_type):
    items = catalog.get("items")
    matches = [item for item in items if item.get("ts_key") == ts_key] if isinstance(items, list) else []
    if len(matches) != 1 or matches[0].get("ts_type") != ts_type:
        raise ValueError("TS 编号或类型与 catalog 不一致")
    tps = tp_json.get("tps")
    if not isinstance(tps, list) or not tps:
        raise ValueError("TP JSON 缺少 tps[]")
    ts = matches[0]
    inputs = [("ts", str(ts.get("ts_name") or ""),
               str(ts.get("resolve_description") or ts.get("description") or ""))]
    inputs += [(str(tp.get("tp_id_temp") or ""), str(tp.get("tpName") or ""),
                str(tp.get("description") or "")) for tp in tps if isinstance(tp, dict)]
    if len(inputs) != len(tps) + 1 or any(not key or not name for key, name, _ in inputs):
        raise ValueError("TS 名称或 TP 临时 ID/名称为空")
    return [(key, (name + " " + description).strip()[:500]) for key, name, description in inputs]


def collect(catalog, tp_json, graph_script, ts_key, ts_type, product, evidence):
    labels = ["TestFactor", "SceneFactor"] if ts_type == "scene" else ["TestFactor"]
    seen = {label: set() for label in labels}
    for key, query in build_queries(catalog, tp_json, ts_key, ts_type):
        for label in labels:
            result = search(graph_script, label, product, query)
            evidence["queries"].append({"target": key, "label": label, "query": query,
                                        "response": result})
            id_field = "test_factor_id" if label == "TestFactor" else "factor_code"
            target = "test_factors" if label == "TestFactor" else "scene_factors"
            for candidate in result["data"]:
                if not isinstance(candidate, dict):
                    raise ValueError(f"{label} 候选不是对象")
                identifier = candidate.get(id_field)
                if identifier and identifier not in seen[label]:
                    evidence[target].append(candidate)
                    seen[label].add(identifier)
    evidence["success"] = True
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("catalog-file", "tp-file", "graph-script", "ts-key", "ts-type",
                 "product", "output"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    output = Path(args.output)
    evidence = {"success": False, "ts_key": args.ts_key, "ts_type": args.ts_type,
                "product": args.product, "queries": [], "test_factors": [], "scene_factors": []}
    try:
        if not args.product.strip() or not Path(args.graph_script).is_file():
            raise ValueError("产品名为空或图谱查询脚本不存在")
        collect(read_json(args.catalog_file), read_json(args.tp_file),
                args.graph_script, args.ts_key, args.ts_type, args.product, evidence)
    except (OSError, ValueError, TypeError) as exc:
        evidence["success"] = False
        evidence["error"] = str(exc)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {"success": evidence["success"], "output": str(output),
               "queries": len(evidence.get("queries", [])),
               "test_factors": len(evidence.get("test_factors", [])),
               "scene_factors": len(evidence.get("scene_factors", []))}
    if not evidence["success"]:
        summary["error"] = evidence["error"]
    print(json.dumps(summary, ensure_ascii=False))
    if not evidence["success"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
