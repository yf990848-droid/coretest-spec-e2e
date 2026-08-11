#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""文件下载分发器 - 根据文档类型选择不同的下载处理方式"""

import argparse
import sys
import os

import dbox_download
from single_file_downloader import SingleDownloader


def download_file(file_id: str, output_dir: str, us_num: str, doc_type: str) -> bool:
    """
    根据文档类型下载文件

    Args:
        file_id: 文件ID
        output_dir: 目标路径
        us_num: 需求编号
        doc_type: 文档类型 (DBOX / IDP)

    Returns:
        下载成功返回True，失败返回False
    """
    doc_type = doc_type.upper()

    if doc_type == "DBOX":
        return download_dbox(file_id, output_dir, us_num)
    elif doc_type == "IDP":
        return download_idp(file_id, output_dir, us_num)
    else:
        print(f"不支持的文档类型: {doc_type}，支持的类型: DBOX, IDP")
        return False


def download_dbox(file_id: str, output_dir: str, us_num: str) -> bool:
    """
    使用DBox方式下载文件

    Args:
        file_id: 文件ID
        output_dir: 输出目录
        us_num: 需求编号

    Returns:
        下载成功返回True，失败返回False
    """
    try:
        print(f"使用DBox方式下载文件: {file_id}")
        saved_path = dbox_download.download_document(file_id, output_dir)
        target_path = os.path.join(output_dir, f"{us_num}.docx")
        if os.path.abspath(saved_path) != os.path.abspath(target_path):
            os.replace(saved_path, target_path)
        print(f"文件下载成功，保存至: {target_path}")
        return True
    except Exception as e:
        print(f"DBox下载失败: {e}")
        return False


def download_idp(file_id: str, output_dir: str, us_num: str) -> bool:
    """
    使用IDP方式下载文件

    Args:
        file_id: 文件ID
        output_dir: 输出目录
        us_num: 需求编号

    Returns:
        下载成功返回True，失败返回False
    """
    try:
        print(f"使用IDP方式下载文件: {file_id}")
        downloader = SingleDownloader()
        result = downloader.download_by_doc_id(file_id, us_num, output_dir)
        if result.success:
            print(f"文件下载成功，保存至: {result.file_path}")
            return True
        else:
            print(f"IDP下载失败: {result.error_message}")
            return False
    except Exception as e:
        print(f"IDP下载失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="文件下载分发器")
    parser.add_argument("--doc-id", "-d", required=True, help="doc文档的ID")
    parser.add_argument("--output-dir", "-o", required=True, help="输出路径")
    parser.add_argument("--us-num", "-u", required=True, help="需求编号")
    parser.add_argument("--doc-type", "-t", required=True, help="文档类型 (DBOX / IDP)")

    args = parser.parse_args()

    success = download_file(
        args.doc_id,
        args.output_dir,
        args.us_num,
        args.doc_type
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
