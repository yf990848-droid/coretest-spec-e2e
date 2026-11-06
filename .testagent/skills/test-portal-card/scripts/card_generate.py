import json
import sys
import uuid
import logging
import os
import getpass
from datetime import datetime

import requests


def setup_logger():
    """设置日志记录器"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(script_dir, 'card_generate.log')

    logger = logging.getLogger('test_portal_card')
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

    # 限制日志文件大小
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if len(lines) > 100:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.writelines(lines[-100:])

    return logger


logger = setup_logger()

# cardName 到 subTitle 的映射
CARD_SUBTITLE_MAP = {
    "coretest-explore": "全量测试设计",
    "coretest-design": "全量测试设计",
    "coretest-archive": "全量测试设计",
}

# 默认版本参数（working 状态时使用，确保 iframe 能立即加载页面）
DEFAULT_VERSION_PBI = "7414819"


def get_user_id():
    """通过 getpass 获取当前用户ID"""
    try:
        user_id = getpass.getuser()
        if user_id:
            return user_id
    except Exception as e:
        logger.warning(f"getpass.getuser() 获取失败: {e}")
    return "w30020094"


def get_version_str():
    """读取 codeagent-extension.json 获取模板名和版本号"""
    current_file = os.path.abspath(__file__)
    script_dir = os.path.dirname(current_file)
    extension_json_path = os.path.join(script_dir, *[os.pardir] * 4, "codeagent-extension.json")

    try:
        with open(extension_json_path, 'r', encoding='utf-8') as f:
            extension_data = json.load(f)
            name = extension_data.get("name", 'testagent-spec-e2e')
            version = extension_data.get("version", "0.0.1")
            return f"{name}@{version}"
    except Exception as e:
        logger.error(f"读取 codeagent-extension.json 文件失败: {e}")
        return "testagent-spec-e2e@0.0.1"


def get_or_create_card_id(card_name: str) -> str:
    """获取已保存的 card_id，没有则生成新的"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    card_id_file = os.path.join(script_dir, f"{card_name}_card_id.txt")

    if os.path.exists(card_id_file):
        with open(card_id_file, "r", encoding="utf-8") as f:
            card_id = f.read().strip()
        if card_id:
            logger.info(f"复用card_id: {card_id}, cardName: {card_name}")
            return card_id

    card_id = str(uuid.uuid1())
    logger.info(f"生成新card_id: {card_id}, cardName: {card_name}")
    save_card_id(card_name, card_id)
    return card_id


def save_card_id(card_name: str, card_id: str):
    """持久化 card_id"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    card_id_file = os.path.join(script_dir, f"{card_name}_card_id.txt")
    if os.path.exists(card_id_file):
        os.remove(card_id_file)
    with open(card_id_file, 'w') as f:
        f.write(card_id)


def post_card(data: dict) -> str:
    """通过 card/cache 接口发送卡片，返回 card_cache_id"""
    url = 'http://127.0.0.1:38101/digital-test/agent/v1/card/cache'
    logger.info(f"开始调用接口: {url}")

    try:
        res = requests.post(url, json=data, timeout=30)
        logger.info(f"接口响应状态码: {res.status_code}")

        res_json = res.json()
        logger.info(f"接口响应内容: {json.dumps(res_json, ensure_ascii=False)}")

        if res_json.get("data") and res_json["data"].get("card_cache_id"):
            card_cache_id = res_json["data"]["card_cache_id"]
            logger.info(f"卡片发送成功, card_cache_id: {card_cache_id}")
            return card_cache_id
        else:
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


def build_card_data(card_name: str, card_id: str, state: str,
                    version_pbi: str, user_id: str, analyse_id: str,
                    page_type: str = "fullTestDesign") -> dict:
    """构建卡片数据"""
    sub_title = CARD_SUBTITLE_MAP.get(card_name, card_name)

    data = {
        "workflowType": "wf1",
        "title": "全量测试设计",
        "subTitle": sub_title,
        "type": "local-iframe",
        "subTitleLink": f"/digital-test/agent/v1/static/{get_version_str()}/webapps/default/index.html",
        "state": state,
        "cardName": card_name,
        "id": card_id,
        "cardId": card_id,
        "data": {
            "versionPbi": version_pbi,
            "userId": user_id,
            "analyseId": analyse_id,
            "pageType": page_type
        }
    }

    return data


def generate_working_card(card_name: str,
                          version_pbi: str = "", analyse_id: str = "",
                          page_type: str = "fullTestDesign", user_id: str = "") -> str:
    """生成 working 状态的卡片，携带版本参数让 iframe 立即加载"""
    logger.info("=" * 50)
    logger.info(f"开始初始化卡片 [working], cardName: {card_name}")

    card_id = get_or_create_card_id(card_name)

    vp = version_pbi or DEFAULT_VERSION_PBI
    ui = user_id or get_user_id()
    ai = analyse_id

    data = build_card_data(card_name, card_id, "working", vp, ui, ai, page_type)
    logger.info(f"卡片数据: {json.dumps(data, ensure_ascii=False)}")
    return post_card(data)


def generate_completed_card(card_name: str,
                            version_pbi: str, analyse_id: str,
                            page_type: str = "fullTestDesign", user_id: str = "") -> str:
    """生成 completed 状态的卡片，携带版本信息覆盖 working 卡片"""
    logger.info("=" * 50)
    logger.info(f"开始生成卡片 [completed], cardName: {card_name}")
    logger.info(f"versionPbi: {version_pbi}, analyseId: {analyse_id}, pageType: {page_type}")

    card_id = get_or_create_card_id(card_name)

    ui = user_id or get_user_id()

    data = build_card_data(card_name, card_id, "completed", version_pbi, ui, analyse_id, page_type)
    logger.info(f"卡片数据: {json.dumps(data, ensure_ascii=False)}")
    return post_card(data)


def main():
    logger.info("")
    logger.info("=" * 80)
    logger.info(f"脚本开始执行: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if len(sys.argv) < 3:
        logger.error("参数不足")
        print(json.dumps({
            "success": False,
            "message": "参数不足。working: card_generate.py working {cardName} [versionPbi] [analyseId] [pageType]; completed: card_generate.py completed {cardName} {versionPbi} {analyseId} [pageType]"
        }))
        return

    state = sys.argv[1]
    card_name = sys.argv[2]

    try:
        if state == "working":
            # working 可选传 versionPbi/analyseId/pageType/userId，不传则用默认值
            vp = sys.argv[3] if len(sys.argv) > 3 else ""
            ai = sys.argv[4] if len(sys.argv) > 4 else ""
            pt = sys.argv[5] if len(sys.argv) > 5 else "fullTestDesign"
            uid = sys.argv[6] if len(sys.argv) > 6 else ""
            card_cache_id = generate_working_card(card_name, vp, ai, pt, uid)
        elif state == "completed":
            if len(sys.argv) < 5:
                logger.error("completed模式参数不足")
                print(json.dumps({
                    "success": False,
                    "message": "completed模式需要: card_generate.py completed {cardName} {versionPbi} {analyseId} [pageType] [userId]"
                }))
                return
            version_pbi = sys.argv[3]
            analyse_id = sys.argv[4]
            pt = sys.argv[5] if len(sys.argv) > 5 else "fullTestDesign"
            uid = sys.argv[6] if len(sys.argv) > 6 else ""
            card_cache_id = generate_completed_card(
                card_name, version_pbi, analyse_id, pt, uid
            )
        else:
            logger.error(f"不支持的状态: {state}")
            print(json.dumps({"success": False, "message": f"不支持的状态: {state}，请使用 working 或 completed"}))
            return

        if card_cache_id:
            output = {
                "success": True,
                "message": "success",
                "data": {
                    "card_cache_id": card_cache_id,
                },
            }
            logger.info("脚本执行成功")
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
        print(json.dumps({"success": False, "message": f"脚本执行异常: {str(e)}"}))

    logger.info(f"脚本执行结束: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    logger.info("")


if __name__ == "__main__":
    main()
