#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministically synchronize CoreTest task/TR/TS Markdown sections to IDP."""

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


SCHEMA_VERSION = 1
TASK_ACTIVITIES = {
    "概述": ["被测对象概述", "测试方案概述"],
    "测试设计策略": [
        "特性风险分析（RBT）",
        "测试重点难点分析",
        "分层测试策略",
        "底层硬件/组网差异测试策略分析",
        "网元形态差异测试策略分析",
    ],
}
TR_ACTIVITIES = ["场景分析", "测试类型分析", "特性交互分析", "功能交互分析", "设计约束分析"]
INTERNAL_DESIGN = "基于业务内部实现的设计"
DFX_TYPES = {"performance", "reliability", "usability", "security", "serviceability", "ai", "funcsafety", "compatibility", "testability", "customized"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON顶层必须是对象: {path}")
    return value


def atomic_write_json(path: Path, value: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
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


def require_text(data: Dict[str, Any], key: str) -> str:
    value = str(data.get(key, "")).strip()
    if not value:
        raise ValueError(f"document_request.json 缺少 {key}")
    return value


def safe_name(value: str) -> str:
    result = re.sub(r"[^0-9A-Za-z._-]+", "_", value).strip("._-") or "item"
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
    return f"{result}_{digest}"


def expected_nodes(scope: Dict[str, Any]) -> List[str]:
    result: List[str] = []
    for kind in ("task", "tr", "ts"):
        values = scope.get(kind)
        if not isinstance(values, list) or not all(isinstance(item, str) and item.strip() for item in values):
            raise ValueError(f"document_scope.{kind} 必须是非空字符串数组或空数组")
        result.extend(f"{kind.upper()}:{item}" for item in values)
    return result


def validate_request(request: Dict[str, Any]) -> Tuple[Path, List[str]]:
    for key in (
        "extension_root", "design_task_id", "pbi", "user_id", "tr_id", "tr_info_file",
        "design_task_info_file", "test_spec_file", "ts_catalog_file", "test_design_dir",
        "archive_state_file", "document_plan_file",
    ):
        require_text(request, key)
    scope = request.get("document_scope")
    if not isinstance(scope, dict) or set(scope) != {"task", "tr", "ts"}:
        raise ValueError("document_scope 必须且只能包含 task、tr、ts")
    if scope["task"] != [str(request["design_task_id"])] or scope["tr"] != [str(request["tr_id"])]:
        raise ValueError("document_scope 必须且只能包含当前 design_task_id 和 tr_id")
    catalog = read_json(Path(request["ts_catalog_file"]))
    catalog_keys = [str(item.get("ts_key", "")) for item in catalog.get("items", []) if isinstance(item, dict)]
    if len(catalog_keys) != len(set(catalog_keys)):
        raise ValueError("ts_catalog.json 包含重复 ts_key")
    requested_ts = scope["ts"]
    if any(item not in catalog_keys for item in requested_ts):
        raise ValueError("document_scope.ts 包含 catalog 外 TS")
    if requested_ts != [item for item in catalog_keys if item in set(requested_ts)]:
        raise ValueError("document_scope.ts 必须按 catalog 顺序去重")
    return Path(request["document_plan_file"]), expected_nodes(scope)


def new_plan(nodes: Sequence[str]) -> Dict[str, Any]:
    timestamp = now_iso()
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pending",
        "expected_nodes": list(nodes),
        "nodes": [
            {
                "node_type": key.split(":", 1)[0],
                "node_id": key.split(":", 1)[1],
                "status": "pending",
                "activities": [],
                "error": None,
                "updated_at": timestamp,
            }
            for key in nodes
        ],
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def save_plan(path: Path, plan: Dict[str, Any]) -> None:
    statuses = [node["status"] for node in plan["nodes"]]
    if any(status == "pending" for status in statuses):
        plan["status"] = "pending"
    elif statuses and all(status == "succeeded" for status in statuses):
        plan["status"] = "succeeded"
    elif statuses and all(status in {"failed", "not_executed"} for status in statuses):
        plan["status"] = "failed"
    else:
        plan["status"] = "partial"
    plan["updated_at"] = now_iso()
    atomic_write_json(path, plan)


def parse_sections(path: Path) -> Dict[str, str]:
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    headings: List[Tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$", line)
        if match:
            headings.append((index, len(match.group(1)), match.group(2).strip()))
    result: Dict[str, str] = {}
    for position, (start, level, title) in enumerate(headings):
        end = len(lines)
        for next_start, next_level, _ in headings[position + 1:]:
            if next_level <= level:
                end = next_start
                break
        body = "\n".join(lines[start + 1:end]).strip()
        if title in result:
            raise ValueError(f"章节标题重复: {path}: {title}")
        result[title] = body
    return result


def exact_content(sections: Dict[str, str], titles: Sequence[str], include_titles: bool) -> str:
    missing = [title for title in titles if not sections.get(title, "").strip()]
    if missing:
        raise ValueError(f"缺少或为空的章节: {', '.join(missing)}")
    parts = []
    for title in titles:
        body = sections[title].strip()
        parts.append(f"### {title}\n\n{body}" if include_titles else body)
    return "\n\n".join(parts)


def ts_activity_names(item: Dict[str, Any]) -> List[str]:
    source = str(item.get("source", "")).strip().lower()
    ts_type = str(item.get("ts_type", "")).strip().lower()
    if source == "platform_dfx" or ts_type in DFX_TYPES:
        return ["测试类型交互设计", INTERNAL_DESIGN]
    if ts_type in {"function", "feature"}:
        return ["功能交互设计", INTERNAL_DESIGN]
    if ts_type == "scene":
        return ["基于业务场景的设计", INTERNAL_DESIGN]
    if ts_type == "constraint":
        return [INTERNAL_DESIGN]
    raise ValueError(f"不支持的 TS 类型: source={source}, ts_type={ts_type}")


def run_coretool(coretool: str, args: Sequence[str], timeout: int) -> Dict[str, Any]:
    command = [coretool, *args]
    try:
        completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
        return {
            "command": command,
            "exit_code": completed.returncode,
            "stdout": completed.stdout.decode("utf-8", errors="replace").strip(),
            "stderr": completed.stderr.decode("utf-8", errors="replace").strip(),
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "exit_code": None,
            "stdout": (exc.stdout or b"").decode("utf-8", errors="replace").strip(),
            "stderr": (exc.stderr or b"").decode("utf-8", errors="replace").strip(),
            "timed_out": True,
        }


def save_response(directory: Path, name: str, response: Dict[str, Any]) -> Path:
    path = directory / f"document_{safe_name(name)}.json"
    atomic_write_json(path, response)
    return path


def response_json(response: Dict[str, Any], operation: str) -> Dict[str, Any]:
    if response["timed_out"]:
        raise TimeoutError(f"{operation} 超过命令时限")
    if response["exit_code"] != 0:
        detail = response["stderr"] or response["stdout"] or "无错误信息"
        raise RuntimeError(f"{operation} 失败: {detail}")
    try:
        value = json.loads(response["stdout"])
    except json.JSONDecodeError as exc:
        raise ValueError(f"{operation} 未返回合法 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{operation} JSON 顶层不是对象")
    return value


def local_idp_doc_id(task_info: Dict[str, Any], design_task_id: str) -> str:
    if str(task_info.get("id", task_info.get("design_task_id", design_task_id))) == design_task_id:
        value = str(task_info.get("idp_doc_id", "")).strip()
        if value:
            return value
    for key in ("items", "tasks"):
        items = task_info.get(key)
        if isinstance(items, list):
            matches = [item for item in items if isinstance(item, dict) and str(item.get("id", item.get("design_task_id", ""))) == design_task_id]
            if len(matches) == 1:
                return str(matches[0].get("idp_doc_id", "")).strip()
    return ""


def resolve_idp_doc_id(request: Dict[str, Any], coretool: str, timeout: int, responses: Path) -> str:
    design_task_id = str(request["design_task_id"])
    task_info = read_json(Path(request["design_task_info_file"]))
    value = local_idp_doc_id(task_info, design_task_id)
    if value:
        return value
    response = run_coretool(coretool, ["coretest", "testdesign", "task", "list", "--version-pbi", str(request["pbi"]), "--output", "json"], timeout)
    save_response(responses, "task_list", response)
    payload = response_json(response, "task list")
    items = payload.get("items")
    if not isinstance(items, list):
        raise ValueError("task list 返回缺少 items 数组")
    matches = [item for item in items if isinstance(item, dict) and str(item.get("id", "")) == design_task_id]
    if len(matches) != 1:
        raise ValueError(f"task list 中 design_task_id={design_task_id} 匹配数量不是 1")
    value = str(matches[0].get("idp_doc_id", "")).strip()
    if not value:
        raise ValueError("匹配任务缺少 idp_doc_id")
    return value


def topic_id(coretool: str, timeout: int, responses: Path, idp_doc_id: str, user_id: str, activity: str, parent: Optional[Tuple[str, str, str]], response_name: str) -> str:
    args = ["coretest", "testdesign", "idp", "topic", "list", "--idp-doc-id", idp_doc_id, "--user-id", user_id, "--activity-name", activity]
    if parent:
        args += ["--parent-activity-id", parent[0], "--parent-activity-name", parent[1], "--parent-activity-type", parent[2]]
    args += ["--output", "json"]
    response = run_coretool(coretool, args, timeout)
    save_response(responses, response_name, response)
    payload = response_json(response, f"topic list: {activity}")
    items = payload.get("items")
    if not isinstance(items, list):
        raise ValueError(f"活动 {activity} 的 topic list 返回缺少 items 数组")
    matches = [
        item
        for item in items
        if isinstance(item, dict)
        and str(item.get("topic_name", "")).strip() == activity
        and str(item.get("topic_id", "")).strip()
        and item.get("deleted", 0) in (0, "0", False)
    ]
    if len(matches) != 1:
        total = (payload.get("pagination") or {}).get("total") if isinstance(payload.get("pagination"), dict) else None
        names = [str(item.get("topic_name", "")) for item in items if isinstance(item, dict)]
        raise ValueError(
            f"活动 {activity} 的有效精确 topic 匹配数量不是 1："
            f"返回 {len(items)} 条，精确匹配 {len(matches)} 条，"
            f"pagination.total={total!r}，topic_name={names}"
        )
    return str(matches[0]["topic_id"]).strip()


def write_activity(coretool: str, timeout: int, payload_dir: Path, responses: Path, idp_doc_id: str, user_id: str, node_type: str, node_id: str, activity: str, content: str, topic: str) -> Dict[str, Any]:
    stable_name = f"coretest-idp|{idp_doc_id}|{node_type}|{node_id}|{activity}"
    source_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, stable_name))
    base = f"{node_type}_{node_id}_{activity}"
    payload_path = payload_dir / f"{safe_name(base)}.json"
    atomic_write_json(payload_path, {
        "topic_id": topic,
        "user_id": user_id,
        "display_type": 3,
        "title": activity,
        "source_value_uuid": source_uuid,
        "text_content": content,
    })
    response = run_coretool(coretool, ["coretest", "testdesign", "idp", "source-data", "write", "--data-file", str(payload_path)], timeout)
    expected = f"Successfully wrote source data to topic {topic}"
    response["expected_topic_id"] = topic
    response["success"] = response["exit_code"] == 0 and not response["timed_out"] and expected in f"{response['stdout']}\n{response['stderr']}"
    response_path = save_response(responses, f"write_{base}", response)
    if not response["success"]:
        if response["timed_out"]:
            raise TimeoutError(f"source-data write: {activity} 超过命令时限")
        raise RuntimeError(f"source-data write: {activity} 未确认成功")
    return {"source_value_uuid": source_uuid, "payload_file": str(payload_path), "response_file": str(response_path)}


def find_node(plan: Dict[str, Any], node_type: str, node_id: str) -> Dict[str, Any]:
    return next(node for node in plan["nodes"] if node["node_type"] == node_type and node["node_id"] == node_id)


def fail_node(node: Dict[str, Any], error: Exception) -> None:
    node["status"] = "failed"
    node["error"] = str(error)
    for activity in node["activities"]:
        if activity["status"] == "pending":
            activity["status"] = "not_executed"
    node["updated_at"] = now_iso()


def sync_node(plan_path: Path, plan: Dict[str, Any], node: Dict[str, Any], activities: List[Tuple[str, str]], parent: Optional[Tuple[str, str, str]], context: Dict[str, Any]) -> None:
    node["activities"] = [{"name": name, "status": "pending", "error": None} for name, _ in activities]
    save_plan(plan_path, plan)
    try:
        topics: Dict[str, str] = {}
        for name, _ in activities:
            topics[name] = topic_id(context["coretool"], context["timeout"], context["responses"], context["idp_doc_id"], context["user_id"], name, parent, f"topic_{node['node_type']}_{node['node_id']}_{name}")
        for name, content in activities:
            current = next(item for item in node["activities"] if item["name"] == name)
            try:
                result = write_activity(context["coretool"], context["timeout"], context["payloads"], context["responses"], context["idp_doc_id"], context["user_id"], node["node_type"], node["node_id"], name, content, topics[name])
                current.update({"status": "succeeded", **result})
                save_plan(plan_path, plan)
            except Exception as exc:
                current["status"] = "failed"
                current["error"] = str(exc)
                raise
        node["status"] = "succeeded"
        node["error"] = None
        node["updated_at"] = now_iso()
    except Exception as exc:
        fail_node(node, exc)
    save_plan(plan_path, plan)


def main() -> None:
    parser = argparse.ArgumentParser(description="同步 CoreTest 设计任务/TR/TS 在线文档")
    parser.add_argument("--request-file", required=True)
    parser.add_argument("--coretool-cmd", required=True)
    parser.add_argument("--command-timeout", type=int, default=120)
    args = parser.parse_args()
    if args.command_timeout <= 0:
        parser.error("--command-timeout 必须大于 0")
    if not Path(args.coretool_cmd).is_absolute():
        parser.error("--coretool-cmd 必须是绝对路径")
    request = read_json(Path(args.request_file).resolve())
    plan_path, nodes = validate_request(request)
    plan = new_plan(nodes)
    save_plan(plan_path, plan)
    response_dir = plan_path.parent / "responses"
    payload_dir = plan_path.parent / "document_payloads"
    response_dir.mkdir(parents=True, exist_ok=True)
    payload_dir.mkdir(parents=True, exist_ok=True)
    try:
        catalog = read_json(Path(request["ts_catalog_file"]))
        idp_doc_id = resolve_idp_doc_id(request, args.coretool_cmd, args.command_timeout, response_dir)
        context = {"coretool": args.coretool_cmd, "timeout": args.command_timeout, "responses": response_dir, "payloads": payload_dir, "idp_doc_id": idp_doc_id, "user_id": str(request["user_id"])}
        try:
            spec_sections = parse_sections(Path(request["test_spec_file"]))
            spec_error: Optional[Exception] = None
        except Exception as exc:
            spec_sections = {}
            spec_error = exc

        task_id = str(request["design_task_id"])
        task_node = find_node(plan, "TASK", task_id)
        try:
            if spec_error:
                raise spec_error
            task_activities = [(name, exact_content(spec_sections, titles, True)) for name, titles in TASK_ACTIVITIES.items()]
            sync_node(plan_path, plan, task_node, task_activities, None, context)
        except Exception as exc:
            fail_node(task_node, exc)
            save_plan(plan_path, plan)

        tr_id = str(request["tr_id"])
        tr_node = find_node(plan, "TR", tr_id)
        try:
            if spec_error:
                raise spec_error
            tr_info = read_json(Path(request["tr_info_file"]))
            tr_name = str(tr_info.get("tr_name", "")).strip()
            if not tr_name:
                raise ValueError("tr_info.json 缺少 tr_name")
            tr_activities = [(name, exact_content(spec_sections, [name], False)) for name in TR_ACTIVITIES]
            sync_node(plan_path, plan, tr_node, tr_activities, (tr_id, tr_name, "TR"), context)
        except Exception as exc:
            fail_node(tr_node, exc)
            save_plan(plan_path, plan)

        catalog_map = {str(item.get("ts_key")): item for item in catalog.get("items", []) if isinstance(item, dict)}
        try:
            state = read_json(Path(request["archive_state_file"]))
            state_error: Optional[Exception] = None
        except Exception as exc:
            state = {}
            state_error = exc
        for ts_key in request["document_scope"]["ts"]:
            node = find_node(plan, "TS", ts_key)
            try:
                if state_error:
                    raise state_error
                item = catalog_map[ts_key]
                ts_name = str(item.get("ts_name", "")).strip()
                if not ts_name:
                    raise ValueError(f"{ts_key} 缺少 ts_name")
                record = (state.get("ts") or {}).get(ts_key)
                if not isinstance(record, dict) or record.get("status") != "succeeded" or not record.get("platform_id"):
                    raise ValueError(f"{ts_key} 没有成功归档的真实平台 ID")
                ts_id = str(record["platform_id"])
                if str(item.get("source", "")) == "platform_dfx" and str(item.get("platform_ts_id", "")) != ts_id:
                    raise ValueError(f"{ts_key} 的 platform_ts_id 与归档状态冲突")
                design_file = Path(request["test_design_dir"]) / f"{ts_key.lower()}_test_design.md"
                sections = parse_sections(design_file)
                names = ts_activity_names(item)
                activities = [(name, exact_content(sections, [name], False)) for name in names]
                sync_node(plan_path, plan, node, activities, (ts_id, ts_name, "TS"), context)
            except Exception as exc:
                fail_node(node, exc)
                save_plan(plan_path, plan)
    except Exception as exc:
        for node in plan["nodes"]:
            if node["status"] == "pending":
                fail_node(node, exc)
        save_plan(plan_path, plan)
    print(json.dumps({"success": plan["status"] == "succeeded", "status": plan["status"], "document_plan": str(plan_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
