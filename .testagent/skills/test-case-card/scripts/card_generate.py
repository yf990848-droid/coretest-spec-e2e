import json
import sys
import uuid
import logging
import os
import re
from datetime import datetime

import requests


def setup_logger():
    """设置日志记录器"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(script_dir, 'card_generate.log')

    logger = logging.getLogger('test_case_review_card_generate')
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    def limit_log_file_size():
        """限制日志文件大小，最多保留100行"""
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if len(lines) > 100:
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines[-100:])

    limit_log_file_size()

    return logger


logger = setup_logger()


def json_loads(input_data):
    try:
        return json.loads(input_data)
    except Exception as e:
        logger.error(f"JSON解析失败: {str(e)}, 输入数据: {input_data}")
        return {}


def extract_ts_id(requirement_number: str) -> str:
    """从 requirement_number 末尾提取 TS 编号。"""
    match = re.search(r"_(ts_\d+)$", requirement_number, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return "测试用例生成"


def get_card_id(requirement_number: str):
    # 从当前脚本的上一个目录的上一个目录下的
    # card-initializer/scripts/test_case/requirement_number_card_id.txt 获取
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    skills_dir = os.path.dirname(skill_dir)
    card_id_file = os.path.join(
        skills_dir,
        "card-initializer",
        "scripts",
        "test_case",
        f"{requirement_number}_card_id.txt"
    )

    # 没有就用 uuid1
    if not os.path.exists(card_id_file):
        return str(uuid.uuid1())

    with open(card_id_file, "r", encoding="utf-8") as f:
        card_id = f.read().strip()

    if card_id:
        logger.info(f"输入card_id: {card_id}, requirement_number: {requirement_number}")
    if not card_id:
        card_id = str(uuid.uuid1())
    return card_id


def get_version_str():
    # 获取当前脚本文件的绝对路径
    current_file = os.path.abspath(__file__)
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(current_file)
    # 向上回溯四级目录，拼接 codeagent-extension.json 的路径
    extension_json_path = os.path.join(
        script_dir,
        *[os.pardir] * 4,
        "codeagent-extension.json"
    )

    try:
        with open(extension_json_path, 'r', encoding='utf-8') as f:
            extension_data = json.load(f)
            name = extension_data.get("name", 'test-design')
            version = extension_data.get("version", "1.0.0")
            return f"{name}@{version}"
    except Exception as e:
        logger.error(f"读取 codeagent-extension.json 文件失败: {e}")
        return "test-design@1.0.0"


def generate_card(
    json_file_path: str,
    spec_info: str,
    cida_info_file_path: str,
    requirement_number_override: str = None
) -> dict:
    logger.info("=" * 50)
    logger.info("开始生成测试用例检视卡片")
    logger.info(f"测试用例检视JSON文件路径: {json_file_path}")
    logger.info(f"Spec文件路径: {spec_info}")
    logger.info(f"CIDA信息文件路径: {cida_info_file_path}")

    # 读取 CIDA 信息文件内容并解析
    cida_info = {}
    if cida_info_file_path:
        try:
            logger.info(f"开始读取CIDA信息文件: {cida_info_file_path}")
            with open(cida_info_file_path, "r", encoding="utf-8") as f:
                cida_info = json_loads(f.read())
            logger.info(f"CIDA信息文件读取成功: {cida_info}")
        except FileNotFoundError as e:
            logger.error(
                f"CIDA信息文件不存在: {cida_info_file_path}, 错误: {str(e)}"
            )
        except Exception as e:
            logger.error(
                f"读取CIDA信息文件失败: {cida_info_file_path}, 错误: {str(e)}"
            )

    # 读取 JSON 文件内容
    try:
        logger.info(f"开始读取文件: {json_file_path}")
        with open(json_file_path, "r", encoding="utf-8") as f:
            review_data = json.load(f)
            test_case_count = review_data.get('test_case_count', 0)
            test_point_count = review_data.get('test_point_count', 0)
            logger.info(
                f"文件读取成功, 测试用例数量: {test_case_count}, "
                f"测试点数量: {test_point_count}"
            )
    except FileNotFoundError as e:
        logger.error(f"文件不存在: {json_file_path}, 错误: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"读取文件失败: {json_file_path}, 错误: {str(e)}")
        return None

    # 读取 spec 文件内容
    spec = ""
    if spec_info:
        try:
            logger.info(f"开始读取spec文件: {spec_info}")
            with open(spec_info, "r", encoding="utf-8") as f:
                spec = f.read()
            logger.info("spec文件读取成功")
        except Exception as e:
            logger.error(f"读取spec文件失败: {str(e)}")
    review_data["spec"] = spec

    # 从 cida_info 中获取关键字段，若 task_id 为空则取 requirement_number
    requirement_number = (
        requirement_number_override
        or cida_info.get("requirement_number", "")
    )
    logger.info(f"最终使用requirement_number: {requirement_number}")

    sub_title = extract_ts_id(requirement_number)
    logger.info(f"卡片副标题: {sub_title}")

    task_id = cida_info.get("task_id", "") or requirement_number
    review_data["requirement_number"] = requirement_number
    platform = cida_info.get("platform", "")
    requirement_id = cida_info.get("requirement_id", "")
    review_data["requirement_id"] = requirement_id
    review_data["platform"] = platform

    if platform == "cloudtest":
        cloud_test_config = cida_info.get("cloudTestConfig", "{}")
        review_data["cloudTestConfig"] = cloud_test_config
        service_id = cloud_test_config.get("serviceId", "")
        review_data["req_id"] = service_id + "_" + requirement_id
        review_data["branchUri"] = cida_info.get("branchUri", "")
        review_data["iterationUri"] = cida_info.get("iterationUri", "")
        review_data["project_id"] = cloud_test_config.get("groupId", "")
    else:
        review_data["cidaProjectConfig"] = cida_info.get(
            "cidaProjectConfig",
            "{}"
        )
        review_data["project_id"] = cida_info.get("project_id", "")
        review_data["req_id"] = task_id

    review_data["requirement_name"] = cida_info.get("requirement_name", "")
    review_data["treeType"] = cida_info.get("treeType", "")
    review_data["reqType"] = cida_info.get("reqType", "")

    card_id = get_card_id(requirement_number)

    data = {
        "workflowType": "wf1",
        "title": "测试设计",
        "subTitle": sub_title,
        "type": "local-iframe",
        "subTitleLink": (
            f"/digital-test/agent/v1/static/{get_version_str()}"
            "/webapps/testCase/index.html"
        ),
        "state": "completed",
        "cardName": "test-case-review",
        "id": card_id,
        "cardId": card_id,
        "data": review_data
    }

    logger.info("卡片数据组装完成")
    logger.info(f"卡片数据: {json.dumps(data, ensure_ascii=False)}")

    url = 'http://127.0.0.1:38101/digital-test/agent/v1/card/cache'
    logger.info(f"开始调用接口: {url}")

    try:
        res = requests.post(url, json=data, timeout=30)
        logger.info(f"接口响应状态码: {res.status_code}")

        res_json = res.json()
        logger.info(f"接口响应内容: {json.dumps(res_json, ensure_ascii=False)}")

        if res_json.get("data") and res_json["data"].get("card_cache_id"):
            card_cache_id = res_json["data"]["card_cache_id"]
            logger.info(f"卡片生成成功, card_cache_id: {card_cache_id}")
            return card_cache_id

        logger.error(f"接口返回数据格式异常: {res_json}")
        return None

    except requests.exceptions.Timeout:
        logger.error("接口调用超时")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"接口调用异常: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"未知异常: {str(e)}")
        return None


def main():
    logger.info("")
    logger.info("=" * 80)
    logger.info(
        f"脚本开始执行: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    """参数校验"""
    if len(sys.argv) < 4:
        message = "参数不足，需要传入 json_file_path、spec_info、cida_info 三个参数"
        logger.error(message)
        print(json.dumps({"success": False, "message": message}, ensure_ascii=False))
        return

    """获取入参参数"""
    json_file_path = sys.argv[1]
    spec_info = sys.argv[2]
    cida_info = sys.argv[3]
    requirement_number_override = sys.argv[4] if len(sys.argv) >= 5 else None

    logger.info(f"接收到参数 - json_file_path: {json_file_path}")
    logger.info(f"接收到参数 - spec_info: {spec_info}")
    logger.info(f"接收到参数 - cida_info: {cida_info}")
    logger.info(
        "接收到参数 - requirement_number_override: "
        f"{requirement_number_override}"
    )

    """组装卡片"""
    try:
        card_cache_id = generate_card(
            json_file_path,
            spec_info,
            cida_info,
            requirement_number_override
        )

        if card_cache_id:
            output = {
                "success": True,
                "message": "success",
                "data": {
                    "card_cache_id": card_cache_id,
                },
            }
            logger.info("脚本执行成功")
            logger.info(f"输出结果: {json.dumps(output, ensure_ascii=False)}")
            print(json.dumps(output, ensure_ascii=False))
        else:
            logger.error("卡片生成失败")
            output = {
                "success": False,
                "message": "卡片生成失败",
                "data": None
            }
            print(json.dumps(output, ensure_ascii=False))

    except Exception as e:
        logger.error(f"脚本执行异常: {str(e)}")
        print(
            json.dumps(
                {"success": False, "message": f"脚本执行异常: {str(e)}"},
                ensure_ascii=False
            )
        )

    logger.info(
        f"脚本执行结束: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    logger.info("=" * 80)
    logger.info("")


if __name__ == "__main__":
    main()
