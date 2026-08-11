#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""coretest-archive 归档状态管理。

本脚本只管理本地状态和 MCP 原始响应，不调用 MCP，不修改 tr_ts.json、
ts_<NN>_tp.json 或 ts_<NN>_tc.json。

状态文件：
    .design_output/<design_task_id>/TR_<tr_id>/archive/archive_state.json

常用命令：
    python archive_state.py init --state-file <path> --design-task-id 2470 \
      --ir-id IR20251206000098 --pbi 266926538 --task-name <name> \
      --creator z00655423 --tr-info-file <path> --tr-ts-file <path> \
      --test-design-dir <path>

    python archive_state.py get --state-file <path> --entity tr --key TR

    python archive_state.py record-success --state-file <path> \
      --entity ts --key TS_01 --platform-id 12345 --parent-key TR \
      --parent-id 67890 --response-file <mcp-response.json>
"""

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


SCHEMA_VERSION = 2
ENTITIES = ("tr", "ts", "tp", "tc")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def output(payload: Dict[str, Any], exit_code: int = 0) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if exit_code:
        raise SystemExit(exit_code)


def fail(message: str, exit_code: int = 1) -> None:
    output({"success": False, "error": message}, exit_code)


def read_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8-sig") as stream:
            value = json.load(stream)
    except FileNotFoundError:
        fail(f"文件不存在: {path}")
    except json.JSONDecodeError as exc:
        fail(f"JSON格式错误: {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"JSON顶层必须是对象: {path}")
    return value


def atomic_write_json(path: Path, value: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def load_state(state_file: Path) -> Dict[str, Any]:
    state = read_json(state_file)
    if state.get("schema_version") != SCHEMA_VERSION:
        fail(
            f"不支持的状态版本: {state.get('schema_version')}，"
            f"当前脚本仅支持 {SCHEMA_VERSION}"
        )
    return state


def save_state(state_file: Path, state: Dict[str, Any]) -> None:
    state["updated_at"] = now_iso()
    atomic_write_json(state_file, state)


def normalize_id(value: str) -> Any:
    text = str(value).strip()
    if not text or text == "0":
        fail("platform-id 必须是有效非零ID")
    if re.fullmatch(r"\d+", text):
        return int(text)
    return text


def safe_name(value: str) -> str:
    name = re.sub(r"[^0-9A-Za-z._-]+", "_", value.strip())
    return name.strip("._-") or "item"


def entity_container(state: Dict[str, Any], entity: str) -> Dict[str, Any]:
    if entity == "tr":
        return state.setdefault("tr", {})
    return state.setdefault(entity, {})


def get_record(state: Dict[str, Any], entity: str, key: str) -> Optional[Dict[str, Any]]:
    container = entity_container(state, entity)
    if entity == "tr":
        return container if container else None
    value = container.get(key)
    return value if isinstance(value, dict) else None


def is_succeeded(record: Optional[Dict[str, Any]], entity: str) -> bool:
    if not record or record.get("status") != "succeeded":
        return False
    if entity == "tc":
        return True
    return bool(record.get("platform_id"))


def set_record(state: Dict[str, Any], entity: str, key: str, record: Dict[str, Any]) -> None:
    if entity == "tr":
        state["tr"] = record
    else:
        state.setdefault(entity, {})[key] = record


def parse_json_source(json_text: Optional[str], json_file: Optional[str]) -> Optional[Any]:
    if json_text and json_file:
        fail("response-json 和 response-file 只能指定一个")
    if json_file:
        path = Path(json_file).resolve()
        try:
            with path.open("r", encoding="utf-8-sig") as stream:
                return json.load(stream)
        except FileNotFoundError:
            fail(f"响应文件不存在: {path}")
        except json.JSONDecodeError as exc:
            fail(f"响应JSON格式错误: {path}: {exc}")
    if json_text:
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as exc:
            fail(f"response-json 格式错误: {exc}")
    return None


def save_response(
    state_file: Path,
    entity: str,
    key: str,
    response: Optional[Any],
    suffix: str = "",
) -> Optional[str]:
    if response is None:
        return None
    response_dir = state_file.parent / "responses"
    response_dir.mkdir(parents=True, exist_ok=True)
    tail = f"_{safe_name(suffix)}" if suffix else ""
    filename = f"{entity}_{safe_name(key)}{tail}.json"
    response_file = response_dir / filename
    atomic_write_json(response_file, response)
    return response_file.relative_to(state_file.parent).as_posix()


def command_init(args: argparse.Namespace) -> None:
    state_file = Path(args.state_file).resolve()
    tr_info_file = Path(args.tr_info_file).resolve()
    tr_info = read_json(tr_info_file)
    tr_id = normalize_id(str(tr_info.get("tr_id", "")))
    context = {
        "design_task_id": int(args.design_task_id),
        "tr_id": tr_id,
        "ir_id": args.ir_id,
        "pbi": int(args.pbi),
        "task_name": args.task_name,
        "creator": args.creator,
    }
    sources = {
        "tr_info_file": str(tr_info_file),
        "tr_ts_file": str(Path(args.tr_ts_file).resolve()),
        "test_design_dir": str(Path(args.test_design_dir).resolve()),
    }
    timestamp = now_iso()
    tr_record = {
        "key": "TR",
        "status": "succeeded",
        "platform_id": tr_id,
        "source": "init",
        "archive_action": "reused",
        "tr_info": tr_info,
        "updated_at": timestamp,
    }

    if state_file.exists():
        state = load_state(state_file)
        old_context = state.get("context", {})
        mismatches = {
            key: {"existing": old_context.get(key), "incoming": value}
            for key, value in context.items()
            if old_context.get(key) != value
        }
        if mismatches:
            fail(f"归档状态与当前上下文不一致: {json.dumps(mismatches, ensure_ascii=False)}")
        old_sources = state.get("sources", {})
        source_mismatches = {
            key: {"existing": old_sources.get(key), "incoming": value}
            for key, value in sources.items()
            if old_sources.get(key) != value
        }
        if source_mismatches:
            fail(f"归档状态与当前输入路径不一致: {json.dumps(source_mismatches, ensure_ascii=False)}")
        state["tr"] = tr_record
        save_state(state_file, state)
        output({"success": True, "created": False, "state_file": str(state_file)})
        return

    state = {
        "schema_version": SCHEMA_VERSION,
        "context": context,
        "sources": sources,
        "request": {
            "requested": [],
            "execution_plan": {"tr": [], "ts": [], "tp": [], "tc": []},
        },
        "tr": tr_record,
        "ts": {},
        "tp": {},
        "tc": {},
        "card": {},
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    atomic_write_json(state_file, state)
    output({"success": True, "created": True, "state_file": str(state_file)})


def command_record_plan(args: argparse.Namespace) -> None:
    state_file = Path(args.state_file).resolve()
    state = load_state(state_file)
    if args.requested or any((args.tr, args.ts, args.tp, args.tc)):
        requested = args.requested
        plan = {
            "tr": args.tr,
            "ts": args.ts,
            "tp": args.tp,
            "tc": args.tc,
        }
    else:
        if not args.requested_json or not args.plan_json:
            fail("必须传入 --requested 及计划参数，或同时传入 --requested-json 和 --plan-json")
        try:
            requested = json.loads(args.requested_json)
            plan = json.loads(args.plan_json)
        except json.JSONDecodeError as exc:
            fail(f"计划JSON格式错误: {exc}")
    if not isinstance(requested, list):
        fail("requested-json 必须是JSON数组")
    if not isinstance(plan, dict):
        fail("plan-json 必须是JSON对象")
    state["request"] = {
        "requested": requested,
        "execution_plan": plan,
        "updated_at": now_iso(),
    }
    save_state(state_file, state)
    output({"success": True, "request": state["request"]})


def command_get(args: argparse.Namespace) -> None:
    state_file = Path(args.state_file).resolve()
    state = load_state(state_file)
    record = get_record(state, args.entity, args.key)
    output({
        "success": True,
        "found": record is not None,
        "entity": args.entity,
        "key": args.key,
        "record": record,
    })


def base_record(previous: Optional[Dict[str, Any]], key: str) -> Dict[str, Any]:
    record = dict(previous or {})
    record.setdefault("key", key)
    record.setdefault("attempts", 0)
    return record


def add_parent(record: Dict[str, Any], args: argparse.Namespace) -> None:
    if getattr(args, "parent_key", None):
        record["parent_key"] = args.parent_key
    if getattr(args, "parent_id", None):
        record["parent_id"] = normalize_id(args.parent_id)


def command_mark_in_progress(args: argparse.Namespace) -> None:
    state_file = Path(args.state_file).resolve()
    state = load_state(state_file)
    previous = get_record(state, args.entity, args.key)
    if is_succeeded(previous, args.entity):
        output({"success": True, "skipped": True, "record": previous})
        return
    record = base_record(previous, args.key)
    record["status"] = "in_progress"
    record["attempts"] = int(record.get("attempts", 0)) + 1
    record["error"] = None
    record["updated_at"] = now_iso()
    add_parent(record, args)
    set_record(state, args.entity, args.key, record)
    save_state(state_file, state)
    output({"success": True, "skipped": False, "record": record})


def command_record_success(args: argparse.Namespace) -> None:
    state_file = Path(args.state_file).resolve()
    state = load_state(state_file)
    previous = get_record(state, args.entity, args.key)
    if args.entity == "tc":
        incoming_id = normalize_id(args.platform_id) if args.platform_id else None
    else:
        if not args.platform_id:
            fail(f"{args.entity} 的 record-success 必须提供 --platform-id")
        incoming_id = normalize_id(args.platform_id)
    if is_succeeded(previous, args.entity):
        if (
            incoming_id is not None
            and previous.get("platform_id") is not None
            and previous.get("platform_id") != incoming_id
        ):
            fail(
                f"对象 {args.entity}:{args.key} 已绑定平台ID "
                f"{previous.get('platform_id')}，拒绝覆盖为 {incoming_id}"
            )
        output({"success": True, "skipped": True, "record": previous})
        return
    record = base_record(previous, args.key)
    record["status"] = "succeeded"
    if incoming_id is not None:
        record["platform_id"] = incoming_id
    else:
        record.pop("platform_id", None)
    record["error"] = None
    record["updated_at"] = now_iso()
    add_parent(record, args)
    response = parse_json_source(args.response_json, args.response_file)
    response_path = save_response(state_file, args.entity, args.key, response)
    if response_path:
        record["response_file"] = response_path
    set_record(state, args.entity, args.key, record)
    save_state(state_file, state)
    output({"success": True, "record": record})


def command_record_failure(args: argparse.Namespace) -> None:
    state_file = Path(args.state_file).resolve()
    state = load_state(state_file)
    previous = get_record(state, args.entity, args.key)
    if is_succeeded(previous, args.entity):
        output({"success": True, "skipped": True, "record": previous})
        return
    record = base_record(previous, args.key)
    record["status"] = "failed"
    record["error"] = args.error
    record["updated_at"] = now_iso()
    add_parent(record, args)
    response = parse_json_source(args.response_json, args.response_file)
    response_path = save_response(state_file, args.entity, args.key, response, "failed")
    if response_path:
        record["response_file"] = response_path
    set_record(state, args.entity, args.key, record)
    save_state(state_file, state)
    output({"success": True, "record": record})


def command_record_blocked(args: argparse.Namespace) -> None:
    state_file = Path(args.state_file).resolve()
    state = load_state(state_file)
    previous = get_record(state, args.entity, args.key)
    if is_succeeded(previous, args.entity):
        output({"success": True, "skipped": True, "record": previous})
        return
    record = base_record(previous, args.key)
    record["status"] = "blocked"
    record["error"] = args.reason
    record["updated_at"] = now_iso()
    add_parent(record, args)
    set_record(state, args.entity, args.key, record)
    save_state(state_file, state)
    output({"success": True, "skipped": False, "record": record})


def command_record_skipped(args: argparse.Namespace) -> None:
    state_file = Path(args.state_file).resolve()
    state = load_state(state_file)
    previous = get_record(state, "tp", args.key)
    if previous and previous.get("status") == "succeeded" and previous.get("platform_id"):
        output({"success": True, "skipped": True, "record": previous})
        return
    record = base_record(previous, args.key)
    record["status"] = "skipped"
    record["error"] = args.reason
    record["updated_at"] = now_iso()
    add_parent(record, args)
    set_record(state, "tp", args.key, record)
    save_state(state_file, state)
    output({"success": True, "skipped": False, "record": record})


def command_record_card(args: argparse.Namespace) -> None:
    state_file = Path(args.state_file).resolve()
    state = load_state(state_file)
    success = args.card_success == "true"
    card = {
        "status": "succeeded" if success else "failed",
        "target_type": args.target_type,
        "target_key": args.target_key,
        "analyse_id": normalize_id(args.analyse_id) if args.analyse_id else None,
        "page_type": args.page_type,
        "card_cache_id": args.card_cache_id or None,
        "error": args.error or None,
        "updated_at": now_iso(),
    }
    response = parse_json_source(args.response_json, args.response_file)
    response_path = save_response(state_file, "card", args.target_key, response)
    if response_path:
        card["response_file"] = response_path
    state["card"] = card
    save_state(state_file, state)
    output({"success": True, "card": card})


def command_summary(args: argparse.Namespace) -> None:
    state_file = Path(args.state_file).resolve()
    state = load_state(state_file)
    counts: Dict[str, Dict[str, int]] = {}
    for entity in ENTITIES:
        if entity == "tr":
            records = [state.get("tr", {})] if state.get("tr") else []
        else:
            records = list(state.get(entity, {}).values())
        entity_counts: Dict[str, int] = {}
        for record in records:
            status = record.get("status", "unknown")
            entity_counts[status] = entity_counts.get(status, 0) + 1
        counts[entity] = entity_counts
    output({
        "success": True,
        "state_file": str(state_file),
        "context": state.get("context", {}),
        "request": state.get("request", {}),
        "counts": counts,
        "card": state.get("card", {}),
    })


def add_state_file(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--state-file", required=True)


def add_entity_key(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--entity", required=True, choices=ENTITIES)
    parser.add_argument("--key", required=True)


def add_parent_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--parent-key")
    parser.add_argument("--parent-id")


def add_response_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--response-json")
    parser.add_argument("--response-file")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="coretest-archive 归档状态管理")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    add_state_file(init)
    init.add_argument("--design-task-id", required=True, type=int)
    init.add_argument("--ir-id", required=True)
    init.add_argument("--pbi", required=True, type=int)
    init.add_argument("--task-name", required=True)
    init.add_argument("--creator", required=True)
    init.add_argument("--tr-info-file", required=True)
    init.add_argument("--tr-ts-file", required=True)
    init.add_argument("--test-design-dir", required=True)
    init.set_defaults(handler=command_init)

    plan = sub.add_parser("record-plan")
    add_state_file(plan)
    plan.add_argument("--requested", action="append", default=[])
    plan.add_argument("--tr", action="append", default=[])
    plan.add_argument("--ts", action="append", default=[])
    plan.add_argument("--tp", action="append", default=[])
    plan.add_argument("--tc", action="append", default=[])
    plan.add_argument("--requested-json")
    plan.add_argument("--plan-json")
    plan.set_defaults(handler=command_record_plan)

    get = sub.add_parser("get")
    add_state_file(get)
    add_entity_key(get)
    get.set_defaults(handler=command_get)

    progress = sub.add_parser("mark-in-progress")
    add_state_file(progress)
    add_entity_key(progress)
    add_parent_args(progress)
    progress.set_defaults(handler=command_mark_in_progress)

    success = sub.add_parser("record-success")
    add_state_file(success)
    add_entity_key(success)
    success.add_argument(
        "--platform-id",
        help="TR/TS/TP 必填且必须为有效非零 ID；TC 可省略",
    )
    add_parent_args(success)
    add_response_args(success)
    success.set_defaults(handler=command_record_success)

    failure = sub.add_parser("record-failure")
    add_state_file(failure)
    add_entity_key(failure)
    failure.add_argument("--error", required=True)
    add_parent_args(failure)
    add_response_args(failure)
    failure.set_defaults(handler=command_record_failure)

    blocked = sub.add_parser("record-blocked")
    add_state_file(blocked)
    add_entity_key(blocked)
    blocked.add_argument("--reason", required=True)
    add_parent_args(blocked)
    blocked.set_defaults(handler=command_record_blocked)

    skipped = sub.add_parser("record-skipped")
    add_state_file(skipped)
    skipped.add_argument("--key", required=True)
    skipped.add_argument("--reason", required=True)
    add_parent_args(skipped)
    skipped.set_defaults(handler=command_record_skipped)

    card = sub.add_parser("record-card")
    add_state_file(card)
    card.add_argument("--card-success", required=True, choices=("true", "false"))
    card.add_argument("--target-type", required=True, choices=("TR", "TS", "TP", "TC"))
    card.add_argument("--target-key", required=True)
    card.add_argument("--analyse-id")
    card.add_argument("--page-type", required=True, choices=("TR", "TS", "TP"))
    card.add_argument("--card-cache-id")
    card.add_argument("--error")
    add_response_args(card)
    card.set_defaults(handler=command_record_card)

    summary = sub.add_parser("summary")
    add_state_file(summary)
    summary.set_defaults(handler=command_summary)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.handler(args)
    except SystemExit:
        raise
    except Exception as exc:
        fail(f"状态操作失败: {exc}")


if __name__ == "__main__":
    main()
