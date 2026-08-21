#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge platform DFX TS records and Explore-generated TS records."""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional


NORMAL_TS_TYPES = {"scene", "function", "feature", "constraint"}


def fail(message: str) -> None:
    raise ValueError(message)


def read_json(path: Optional[Path]) -> dict[str, Any]:
    try:
        if path is None:
            value = json.load(sys.stdin)
        else:
            value = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        fail(f"文件不存在: {path}")
    except json.JSONDecodeError as exc:
        fail(f"JSON格式错误: {path or 'stdin'}: {exc}")
    if not isinstance(value, dict):
        fail(f"JSON顶层必须是对象: {path or 'stdin'}")
    return value


def get_field(item: dict[str, Any], *names: str) -> Any:
    lowered = {str(key).lower(): value for key, value in item.items()}
    for name in names:
        if name in item:
            return item[name]
        if name.lower() in lowered:
            return lowered[name.lower()]
    return None


def ts_key(index: int) -> str:
    return f"TS_{index:02d}"


def build_catalog(platform: dict[str, Any], tr_ts: dict[str, Any]) -> dict[str, Any]:
    platform_items = platform.get("items")
    normal_specs = tr_ts.get("test_specs")
    if not isinstance(platform_items, list):
        fail("平台查询结果缺少 items 数组")
    if not isinstance(normal_specs, list):
        fail("tr_ts.json 缺少 test_specs 数组")

    tr = tr_ts.get("tr") or {}
    if not isinstance(tr, dict) or not tr.get("tr_id"):
        fail("tr_ts.json 缺少 tr.tr_id")

    items: list[dict[str, Any]] = []
    platform_ids: set[str] = set()

    for platform_index, raw in enumerate(platform_items):
        if not isinstance(raw, dict):
            fail(f"平台 items[{platform_index}] 必须是对象")
        current_type = str(get_field(raw, "ts_type", "type") or "").strip()
        if not current_type:
            fail(f"平台 items[{platform_index}] 缺少 ts_type")
        if current_type.lower() in NORMAL_TS_TYPES:
            continue

        platform_id = str(get_field(raw, "id", "ts_id") or "").strip()
        if not platform_id:
            fail(f"平台 DFX items[{platform_index}] 缺少 id")
        if platform_id in platform_ids:
            fail(f"平台 DFX TS ID 重复: {platform_id}")
        platform_ids.add(platform_id)

        entry = dict(raw)
        entry.update({
            "ts_key": ts_key(len(items) + 1),
            "source": "platform_dfx",
            "platform_ts_id": platform_id,
            "platform_ts_no": str(get_field(raw, "ts_no") or ""),
            "ts_type": current_type,
            "ts_name": str(get_field(raw, "ts_name", "name") or ""),
            "platform_index": platform_index,
        })
        items.append(entry)

    dfx_count = len(items)
    for normal_index, raw in enumerate(normal_specs):
        if not isinstance(raw, dict):
            fail(f"tr_ts.json test_specs[{normal_index}] 必须是对象")
        current_type = str(raw.get("ts_type") or "").strip()
        if current_type.lower() not in NORMAL_TS_TYPES:
            fail(
                f"普通 TS test_specs[{normal_index}] 的 ts_type={current_type!r} 非法，"
                f"只允许 {sorted(NORMAL_TS_TYPES)}"
            )
        entry = dict(raw)
        entry.update({
            "ts_key": ts_key(dfx_count + normal_index + 1),
            "source": "explore",
            "tr_ts_index": normal_index,
            "ts_type": current_type,
            "ts_name": str(raw.get("ts_name") or ""),
        })
        items.append(entry)

    return {
        "_meta": {
            "schema_version": 1,
            "source": "coretest-explore / build_ts_catalog.py",
            "ordinary_types": sorted(NORMAL_TS_TYPES),
        },
        "tr_id": tr.get("tr_id"),
        "dfx_count": dfx_count,
        "normal_count": len(normal_specs),
        "total_count": len(items),
        "items": items,
    }


def atomic_write(path: Path, value: dict[str, Any]) -> None:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="生成当前 TR 的统一 TS 编号目录")
    parser.add_argument("--platform-json", required=True, help="query-by-type 的 JSON 输出文件；- 表示 stdin")
    parser.add_argument("--tr-ts-json", required=True, help="Explore 生成的 tr_ts.json")
    parser.add_argument("--output", required=True, help="输出 ts_catalog.json")
    args = parser.parse_args()

    try:
        platform_path = None if args.platform_json == "-" else Path(args.platform_json).resolve()
        tr_ts_path = Path(args.tr_ts_json).resolve()
        output_path = Path(args.output).resolve()
        catalog = build_catalog(read_json(platform_path), read_json(tr_ts_path))
        atomic_write(output_path, catalog)
        print(json.dumps({
            "success": True,
            "output": str(output_path),
            "dfx_count": catalog["dfx_count"],
            "normal_count": catalog["normal_count"],
            "total_count": catalog["total_count"],
        }, ensure_ascii=False))
    except ValueError as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False), file=os.sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
