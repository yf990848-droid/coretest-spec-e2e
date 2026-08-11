#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""按文档类型下载唯一命名的需求文档，并以 JSON 返回结果。"""

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

import dbox_download
from single_file_downloader import SingleDownloader

SUPPORTED_TYPES = {"DBOX", "IDP"}
SAFE_PART = re.compile(r"^[A-Za-z0-9._-]+$")


def emit(payload: dict) -> None:
    """最后一行输出稳定 JSON，便于上游解析。"""
    print(json.dumps(payload, ensure_ascii=False))


def validate_part(name: str, value: str) -> str:
    value = str(value or "").strip()
    if not value or not SAFE_PART.fullmatch(value) or value in {".", ".."}:
        raise ValueError(f"{name} 包含非法文件名字符或为空: {value!r}")
    return value


def ensure_file(path: Path) -> Path:
    path = path.resolve()
    if not path.is_file() or path.stat().st_size <= 0:
        raise RuntimeError(f"下载结果不存在或为空: {path}")
    return path


def reuse_or_reject(target: Path) -> Path | None:
    if not target.exists():
        return None
    if target.is_file() and target.stat().st_size > 0:
        return target.resolve()
    raise RuntimeError(f"目标已存在但不是可复用的非空文件: {target}")


def download_dbox(file_id: str, target: Path) -> Path:
    # DBOX 的底层下载器决定临时文件名，因此先落独立目录，再移动到唯一目标。
    with tempfile.TemporaryDirectory(prefix="coretest_dbox_") as temp_dir:
        saved = ensure_file(Path(dbox_download.download_document(file_id, temp_dir)))
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(saved), str(target))
    return ensure_file(target)


def download_idp(file_id: str, source_requirement: str, target: Path) -> Path:
    with tempfile.TemporaryDirectory(prefix="coretest_idp_") as temp_dir:
        result = SingleDownloader().download_by_doc_id(file_id, source_requirement, temp_dir)
        if not result.success:
            raise RuntimeError(result.error_message or "IDP 下载失败")
        saved = ensure_file(Path(result.file_path))
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(saved), str(target))
    return ensure_file(target)


def download_file(file_id: str, output_dir: str, source_requirement: str, doc_type: str) -> dict:
    file_id = validate_part("doc_id", file_id)
    source_requirement = validate_part("source_requirement", source_requirement)
    doc_type = validate_part("doc_type", doc_type).upper()
    if doc_type not in SUPPORTED_TYPES:
        raise ValueError(f"不支持的文档类型: {doc_type}，仅支持 DBOX、IDP")

    output = Path(output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    target = output / f"{source_requirement}_{doc_type}_{file_id}.docx"
    reused = reuse_or_reject(target)
    if reused:
        final_path = reused
        status = "reused"
    elif doc_type == "DBOX":
        final_path = download_dbox(file_id, target)
        status = "downloaded"
    else:
        final_path = download_idp(file_id, source_requirement, target)
        status = "downloaded"

    return {
        "success": True,
        "doc_id": file_id,
        "doc_type": doc_type,
        "source_requirement": source_requirement,
        "file_name": final_path.name,
        "file_path": str(final_path),
        "status": status,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="文件下载分发器")
    parser.add_argument("--doc-id", "-d", required=True, help="文档 ID")
    parser.add_argument("--output-dir", "-o", required=True, help="输出目录")
    parser.add_argument("--us-num", "-u", required=True, help="首次关联需求编号（兼容旧参数名）")
    parser.add_argument("--doc-type", "-t", required=True, help="文档类型：DBOX 或 IDP")
    args = parser.parse_args()

    try:
        result = download_file(args.doc_id, args.output_dir, args.us_num, args.doc_type)
        emit(result)
    except Exception as exc:
        emit({
            "success": False,
            "doc_id": args.doc_id,
            "doc_type": str(args.doc_type).upper(),
            "source_requirement": args.us_num,
            "error": str(exc),
        })
        sys.exit(1)


if __name__ == "__main__":
    main()
