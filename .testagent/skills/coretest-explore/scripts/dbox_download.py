#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DBox文档下载脚本"""

import argparse
import sys
import os
import requests


def get_dynamic_token() -> str:
    """获取生产环境的动态token"""
    api_url = "http://oauth2.huawei.com/ApiCommonQuery/appToken/getRestAppDynamicToken"
    body = {
        "credential": "cUJYVGdKN1lVXzBRZHRYdUNzd2g0Nm1aV1R2VXB1WVpvSTFRTmxicWh6YmV2Uy0zdlJ1UXQ4WHVNeXBKLW9qWDZEc0hwMzktd3JtQmpHamxyekx1RFE=",
        "appId": "com.huawei.ipd.coretool.coremlops"
    }

    response = requests.post(api_url, json=body)
    response.raise_for_status()
    result = response.json()

    if result.get("status", {}).get("statusCode") != "SUCCESS":
        error_msg = result.get("status", {}).get("errorMsg", "未知错误")
        raise RuntimeError(f"获取token失败: {error_msg}")

    return result["result"]


def download_document(document_id: str, save_dir: str = ".") -> str:
    """调用DBox下载接口下载Word文档"""
    api_url = "http://api.dbox.huawei.com/Ipdnext/servlet/rest/soaservices/document/downloadForServer"

    token = get_dynamic_token()

    headers = {
        "X-Huawei-Auth": token,
        "Authorization": "Basic bDAwODI2ODc5OjIyMjA3MTgtbHpxag=="
    }

    params = {
        "extra": 1,
        "userName": "pub_IDTCone",
        "docNumber": document_id
    }

    response = requests.post(api_url, headers=headers, params=params, stream=True)
    response.raise_for_status()

    disposition = response.headers.get("Content-Disposition", "")
    filename = f"{document_id}.docx"
    if "filename" in disposition:
        for part in disposition.split(";"):
            part = part.strip()
            if part.startswith("filename*"):
                value = part.split("=")[1].strip().rstrip('"')
                if "utf-8''" in value:
                    filename = value.split("''")[1]
                    break
            elif part.startswith("filename"):
                filename = part.split("=")[1].strip().strip('"')
                break

    if not filename.lower().endswith((".docx", ".doc")):
        filename = f"{document_id}.docx"

    save_path = os.path.join(save_dir, filename)
    os.makedirs(save_dir, exist_ok=True)

    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return save_path


def main():
    parser = argparse.ArgumentParser(description="DBox文档下载脚本")
    parser.add_argument("--document-id", "-d", required=True, help="要下载的文档ID")
    parser.add_argument("--output-dir", "-o", default=".", help="保存目录 (默认: 当前目录)")

    args = parser.parse_args()

    try:
        saved_path = download_document(args.document_id, args.output_dir)
        print(f"文档下载成功，保存至: {saved_path}")
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
