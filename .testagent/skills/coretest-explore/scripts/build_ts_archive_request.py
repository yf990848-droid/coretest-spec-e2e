#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build an Explore TS-only archive request from the stable TS catalog."""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict


def fail(message: str) -> None:
    raise ValueError(message)


def read_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="从 ts_catalog.json 生成 Explore 普通 TS-only 归档计划"
    )
    parser.add_argument("--catalog", required=True, help="ts_catalog.json 路径")
    parser.add_argument("--output", required=True, help="request_plan.json 输出路径")
    args = parser.parse_args()

    try:
        catalog_path = Path(args.catalog).resolve()
        output_path = Path(args.output).resolve()
        catalog = read_json(catalog_path)
        items = catalog.get("items")
        if not isinstance(items, list):
            fail("ts_catalog.json 缺少 items 数组")

        seen = set()
        archive_ts = []
        skipped_dfx = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                fail(f"items[{index}] 必须是对象")
            ts_key = str(item.get("ts_key", "")).strip()
            source = str(item.get("source", "")).strip()
            if not ts_key:
                fail(f"items[{index}] 缺少 ts_key")
            if ts_key in seen:
                fail(f"ts_catalog.json 包含重复 ts_key: {ts_key}")
            seen.add(ts_key)

            if source == "explore":
                if item.get("tr_ts_index") is None:
                    fail(f"{ts_key} 缺少 tr_ts_index")
                archive_ts.append(ts_key)
            elif source == "platform_dfx":
                platform_id = str(item.get("platform_ts_id", "")).strip()
                if not platform_id or platform_id == "0":
                    fail(f"{ts_key} 缺少有效 platform_ts_id")
                skipped_dfx.append(ts_key)
            else:
                fail(f"{ts_key} 的 source 不受支持: {source}")

        if len(items) != len(archive_ts) + len(skipped_dfx):
            fail("catalog 数量与普通 TS、DFX 分类数量不一致")

        request = {
            "requested": ["TS"],
            "execution_plan": {
                "tr": [],
                "ts": archive_ts,
                "tp": [],
                "tc": [],
            },
        }
        atomic_write_json(output_path, request)
        print(json.dumps({
            "success": True,
            "catalog_ts_count": len(items),
            "archive_ts_count": len(archive_ts),
            "skipped_dfx_count": len(skipped_dfx),
            "archive_ts": archive_ts,
            "skipped_dfx": skipped_dfx,
            "request_file": str(output_path),
        }, ensure_ascii=False))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
