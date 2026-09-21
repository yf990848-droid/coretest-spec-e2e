#!/usr/bin/env python3
"""Archive planned TS factors and create new TPs with their factor relations."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from archive_state import atomic_write_json, load_state, now_iso, safe_name, save_state

DESIGN_SCRIPTS = Path(__file__).resolve().parents[2] / "coretest-design" / "scripts"
sys.path.insert(0, str(DESIGN_SCRIPTS))
from factor_plan import read_json, require, validate  # noqa: E402


SOURCE_TYPES = {
    "功能交互设计-功能与测试因子": "function_and_test_factor_type",
    "基于业务内部实现设计—测试因子": "business_test_factor_type",
    "基于业务场景设计—场景因子": "business_scenario_factor",
    "测试类型交互设计—测试因子": "test_type_test_factor_type",
    "测试类型交互设计—测试设计准则": "test_type_test_design_principle",
    "测试类型交互设计—模式库": "test_type_model_lib",
}


class CliError(ValueError):
    def __init__(self, message, response):
        super().__init__(message)
        self.response = response


def run_cli(cli, *args):
    completed = subprocess.run([str(cli), *map(str, args)], capture_output=True,
                               text=True, encoding="utf-8", errors="replace", check=False)
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError:
        data = {"stdout": completed.stdout.strip()}
    if completed.returncode:
        raise CliError(f"CLI exit={completed.returncode}: {completed.stderr.strip() or data}",
                       {"exit_code": completed.returncode, "stdout": completed.stdout,
                        "stderr": completed.stderr, "data": data})
    if isinstance(data, dict) and (data.get("success") is False or data.get("error")):
        raise CliError(f"CLI 返回错误: {data}", data)
    return data


def save_evidence(state_file, kind, key, request, response):
    directory = state_file.parent / "responses"
    directory.mkdir(parents=True, exist_ok=True)
    prefix = f"{kind}_{safe_name(key)}"
    request_file = directory / f"{prefix}_request.json"
    response_file = directory / f"{prefix}_response.json"
    atomic_write_json(request_file, request)
    atomic_write_json(response_file, response)
    return (request_file.relative_to(state_file.parent).as_posix(),
            response_file.relative_to(state_file.parent).as_posix())


def check_context(args):
    state = load_state(args.state_file)
    require(state.get("context", {}).get("pbi") == args.pbi, "状态 PBI 不一致")
    if args.action == "create-tp":
        require(str(state.get("context", {}).get("tr_id")) == str(args.tr_id),
                "状态 TR ID 不一致")
    require(args.ts_key in state.get("request", {}).get("execution_plan", {}).get("ts", []),
            "TS 不在本次锁定的归档计划中")
    ts = state.get("ts", {}).get(args.ts_key, {})
    require(ts.get("status") == "succeeded" and str(ts.get("platform_id")) == str(args.ts_id),
            "TS 尚未成功归档或真实 ID 不一致")
    return state


def cli_list(cli, kind, ts_id):
    group = "scene-factor" if kind == "scene" else "factor"
    args = ("coretest", "testdesign", "asset", group, "list", "--ts-id", ts_id,
            "--output", "json")
    result = run_cli(cli, *args)
    require(isinstance(result, dict) and isinstance(result.get("items"), list),
            f"{group} list 未返回 items[]")
    pagination = result.get("pagination", {})
    total = pagination.get("total", len(result["items"]))
    page_size = pagination.get("page_size", len(result["items"]))
    page = pagination.get("page", 1)
    require(isinstance(total, int) and isinstance(page_size, int) and\n            (page_size > 0 or (total == 0 and page_size == 0)),
            f"{group} list 分页信息无效")
    while len(result["items"]) < total:
        page += 1
        next_page = run_cli(cli, *args, "--page", page, "--page-size", page_size)
        require(isinstance(next_page, dict) and isinstance(next_page.get("items"), list)
                and next_page["items"], f"{group} list 分页查询失败")
        result["items"].extend(next_page["items"])
    return result


def contains(items, kind, factor):
    if kind == "test":
        return any(str(item.get("test_factor_id") or item.get("testFactorId")) == factor["testFactorId"]
                   for item in items)
    for item in items:
        code = (item.get("factor_code") or item.get("factorCode") or
                item.get("scene_factor_code") or item.get("sceneFactorCode") or
                item.get("number"))
        if code:
            if str(code) == factor["factorCode"]:
                return True
        elif (item.get("factor_name") or item.get("factorName") or item.get("name")) == factor["factorName"]:
            return True
    return False


def record_factor(state_file, key, status, ts_id, request, response, error=None):
    state = load_state(state_file)
    previous = state.setdefault("factor", {}).get(key, {})
    request_file, response_file = save_evidence(state_file, "factor", key, request, response)
    state["factor"][key] = {
        "key": key, "status": status, "parent_id": ts_id,
        "attempts": previous.get("attempts", 0) + 1,
        "request_file": request_file, "response_file": response_file,
        "error": error, "updated_at": now_iso(),
    }
    save_state(state_file, state)


def sync_ts(args, plan):
    check_context(args)
    results = []
    for kind, factors in (("test", plan["test_factors"]), ("scene", plan["scene_factors"])):
        for factor in factors:
            identifier = factor["testFactorId"] if kind == "test" else factor["factorCode"]
            key = f"{args.ts_key}/{kind}/{identifier}"
            request = {"ts_id": args.ts_id, "pbi": args.pbi, "kind": kind, "factor": factor}
            try:
                before = cli_list(args.cli, kind, args.ts_id)
                if contains(before["items"], kind, factor):
                    response = {"already_exists": True, "list": before}
                else:
                    payload = {field: value for field, value in factor.items()
                               if field != "factorType"}
                    payload_file = args.state_file.parent / "responses" / f"factor_{safe_name(key)}_payload.json"
                    atomic_write_json(payload_file, [payload])
                    command = ["coretest", "testdesign", "asset",
                               "factor" if kind == "test" else "scene-factor", "create",
                               "--ts-id", args.ts_id, "--pbi", args.pbi,
                               "--asso-act-type", factor["assoActType"]]
                    if kind == "test":
                        command += ["--factor-type", factor["factorType"],
                                    "--factor-file", str(payload_file)]
                    else:
                        command += ["--source-type", factor["sourceType"],
                                    "--scene-factor-file", str(payload_file)]
                    created = run_cli(args.cli, *command)
                    after = cli_list(args.cli, kind, args.ts_id)
                    require(contains(after["items"], kind, factor),
                            f"{key} 创建返回后查询不到对应关系")
                    response = {"create": created, "list": after}
                record_factor(args.state_file, key, "succeeded", args.ts_id, request, response)
                results.append({"key": key, "status": "succeeded"})
            except (OSError, ValueError) as exc:
                record_factor(args.state_file, key, "failed", args.ts_id, request,
                              getattr(exc, "response", {"error": str(exc)}), str(exc))
                results.append({"key": key, "status": "failed", "error": str(exc)})
    return {"success": True, "results": results}


def requirement_alm_ids(tp, tr_info):
    ids = tp.get("requirement_ids") or []
    if isinstance(ids, str):
        ids = [value.strip() for value in ids.split(",") if value.strip()]
    require(isinstance(ids, list), "TP requirement_ids 格式错误")
    mapping = {str(item["requirement_number"]): item.get("requirement_id")
               for item in tr_info.get("requirements", [])}
    require(all(number in mapping and mapping[number] for number in ids),
            "TP 需求编号在 tr_info.json 中缺少对应的 ALM ID")
    return [str(mapping[number]) for number in ids]


def list_all_tps(cli, ts_id):
    args = ("coretest", "testdesign", "tp", "list", "--ts-id", ts_id,
            "--output", "json")
    result = run_cli(cli, *args)
    require(isinstance(result, dict) and isinstance(result.get("items"), list),
            "TP list 未返回 items[]")
    items = list(result["items"])
    pagination = result.get("pagination", {})
    total = pagination.get("total", len(items))
    page_size = pagination.get("page_size", len(items))
    page = pagination.get("page", 1)
    require(isinstance(total, int) and isinstance(page_size, int) and\n            (page_size > 0 or (total == 0 and page_size == 0)),
            "TP list 分页信息无效")
    while len(items) < total:
        page += 1
        next_page = run_cli(cli, *args, "--page", page, "--page-size", page_size)
        require(isinstance(next_page, dict) and isinstance(next_page.get("items"), list)
                and next_page["items"], "TP list 分页查询失败")
        items.extend(next_page["items"])
    require(len(items) >= total, "TP list 返回不完整")
    return items


def create_tp(args, plan, tp_json):
    state = check_context(args)
    key = f"{args.ts_key}/{args.tp_id_temp}"
    require(key in state.get("request", {}).get("execution_plan", {}).get("tp", []),
            "TP 不在本次锁定的归档计划中")
    previous = state.get("tp", {}).get(key, {})
    if previous.get("status") == "succeeded" and previous.get("platform_id"):
        return {"success": True, "skipped": True, "id": previous["platform_id"]}
    require(args.idp_doc_id.strip(), "IDP 文档 ID 不能为空")
    tp = next(item for item in tp_json["tps"] if item["tp_id_temp"] == args.tp_id_temp)
    source_type = SOURCE_TYPES.get(tp.get("tpSourceType"))
    require(source_type, "TP tpSourceType 无法映射为 CLI 来源类型")
    selections = plan["tp_factors"][args.tp_id_temp]
    tests = {factor["testFactorId"]: factor for factor in plan["test_factors"]}
    scenes = {factor["factorCode"]: factor for factor in plan["scene_factors"]}
    relations = {
        "testFactorIdList": [{k: v for k, v in tests[identifier].items() if k != "factorType"}
                             for identifier in selections["test_factor_ids"]],
        "sceneFactorIdList": [scenes[code] for code in selections["scene_factor_codes"]],
        "tpAssociationRequirementAlmIdList": requirement_alm_ids(tp, read_json(args.tr_info_file)),
    }
    name = tp["tpName"]
    existing = list_all_tps(args.cli, args.ts_id)
    require(not any(item.get("tp_name") == name for item in existing),
            "同名 TP 已存在但本地无成功状态，需人工核对，禁止重复创建")
    command = ["coretest", "testdesign", "tp", "create",
               "--version-pbi", args.pbi, "--ts-id", args.ts_id,
               "--tp-type", tp["tpType"], "--tp-source-type", source_type,
               "--parent-tr-id", args.tr_id, "--name", name,
               "--creator", tp.get("creator") or args.creator,
               "--idp-doc-id", args.idp_doc_id,
               "--relations", json.dumps(relations, ensure_ascii=False, separators=(",", ":")),
               "--output", "json"]
    for option, field in (("--description", "description"),
                          ("--resolve-description", "resolveDescription")):
        if tp.get(field):
            command += [option, tp[field]]
    request = {"command": command[:command.index("--relations")], "relations": relations,
               "description": tp.get("description"),
               "resolveDescription": tp.get("resolveDescription")}
    try:
        result = run_cli(args.cli, *command)
        identifier = result.get("id") if isinstance(result, dict) else None
        require(identifier and str(identifier).isdigit() and int(identifier) > 0,
                "CLI 未返回有效 TP ID")
        request_file, response_file = save_evidence(args.state_file, "tp_cli", key, request, result)
        return {"success": True, "id": int(identifier), "request_file": request_file,
                "response_file": response_file}
    except (OSError, ValueError) as exc:
        request_file, response_file = save_evidence(args.state_file, "tp_cli", key, request,
                                                    getattr(exc, "response", {"error": str(exc)}))
        return {"success": False, "error": str(exc), "request_file": request_file,
                "response_file": response_file}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("sync-ts", "create-tp"):
        command = sub.add_parser(action)
        command.add_argument("--cli", required=True, type=Path)
        command.add_argument("--state-file", required=True, type=Path)
        command.add_argument("--plan-file", required=True, type=Path)
        command.add_argument("--tp-file", required=True, type=Path)
        command.add_argument("--ts-key", required=True)
        command.add_argument("--ts-type", required=True)
        command.add_argument("--ts-id", type=int, required=True)
        command.add_argument("--pbi", type=int, required=True)
        command.add_argument("--max-ts-factors", type=int)
        command.add_argument("--max-tp-factors", type=int)
    tp = sub.choices["create-tp"]
    for flag in ("tr-id", "creator", "idp-doc-id", "tp-id-temp", "tr-info-file"):
        tp.add_argument("--" + flag, required=True)
    args = parser.parse_args()
    try:
        plan, tp_json = read_json(args.plan_file), read_json(args.tp_file)
        validate(plan, tp_json, args.ts_key, args.ts_type,
                 args.max_ts_factors, args.max_tp_factors)
        require(all(str(factor["pbi"]) == str(args.pbi) for factor in
                    plan["test_factors"] + plan["scene_factors"]),
                "因子计划的 PBI 与归档上下文不一致")
        result = sync_ts(args, plan) if args.action == "sync-ts" else create_tp(args, plan, tp_json)
        print(json.dumps(result, ensure_ascii=False))
    except (OSError, ValueError, TypeError, KeyError, StopIteration, json.JSONDecodeError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
