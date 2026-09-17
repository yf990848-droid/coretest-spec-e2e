#!/usr/bin/env python3
import warnings
warnings.filterwarnings("ignore")
import requests
from fastmcp import FastMCP
from typing import Any
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from urllib.parse import quote
import binascii

mcp = FastMCP("TestDesignMcp")

BASE_URL = "https://testdesign.cloudspider.rnd.huawei.com"
API_V2 = "/test_design/v1"

PBI_BASE_URL = "https://backend.pipeline-x.rnd.huawei.com/api/v1"
PBI_TOKEN = "d97f4d643a45c593e00390c3a139373d021015a3d4498750021f965debb2e0acff87857ca97e29168e644d286f98bf383060d37cbf71d438f8239ef4a7cff2878be10ad0fb8a3daa4076b34f195eebc2ee270f6614425c90fad84da0a9ea936173b8d663c43b582b55c0b70536405de8d1da8273455d4853cd2e1edf894462ad063798a5bd1cb50ca345740f10274e1cfd3f3614d1fbfe816d08139b161c3f3aaeb0b4b08af81c13d7ec53bd3e8daef0"

class Aes256Encryptor:
    _secret = 'CloudSpider12345'
    _key = bytes(_secret, 'utf-8')[:32].ljust(32, b'\0')

    @classmethod
    def encrypt(cls, data: str) -> str:
        cipher = Cipher(algorithms.AES(cls._key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        data_bytes = bytes(data, 'utf-8')
        padding_len = 16 - (len(data_bytes) % 16)
        data_bytes += bytes([padding_len] * padding_len)
        data_encrypt = encryptor.update(data_bytes) + encryptor.finalize()
        return binascii.b2a_hex(data_encrypt).decode()

    @classmethod
    def decrypt(cls, encrypted_hex: str) -> str:
        cipher = Cipher(algorithms.AES(cls._key), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        encrypted_bytes = binascii.unhexlify(encrypted_hex)
        decrypted = decryptor.update(encrypted_bytes) + decryptor.finalize()
        padding_len = decrypted[-1]
        return decrypted[:-padding_len].decode('utf-8')

class TestDesignClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.timeout = 120.0

    def close(self):
        self.session.close()

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        return self.session.request(method, url, timeout=self.timeout, **kwargs)

    def get_pbi_id(self, product_name: str) -> dict[str, Any]:
        url = f"{PBI_BASE_URL}/pbi/id"
        headers = {"PRIVATE-TOKEN": Aes256Encryptor.decrypt(PBI_TOKEN)}
        response = self._request("POST", url, json={"product": product_name}, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_requirement_infos(self, design_task_id: int) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/requirement/infos"
        response = self._request("GET", url, params={"designTaskId": design_task_id})
        response.raise_for_status()
        return response.json()

    def get_feature_infos(self, design_task_id: int) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/requirement/featureInfos"
        response = self._request("GET", url, params={"designTaskId": design_task_id})
        response.raise_for_status()
        return response.json()

    def get_function_infos(self, design_task_id: int) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/requirement/functionInfos"
        response = self._request("GET", url, params={"designTaskId": design_task_id})
        response.raise_for_status()
        return response.json()

    def get_tr_infos(self, design_task_id: int) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/tr"
        response = self._request("GET", url, params={"designTaskId": design_task_id})
        response.raise_for_status()
        return response.json()

    def get_tr_relative_scene(self, tr_id: int) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/v1/scene_analysis/relativeTrScene"
        response = self._request("GET", url, params={"trId": tr_id})
        response.raise_for_status()
        return response.json()

    def get_tr_relative_function(self, tr_id: int) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/tr/relativeFunctionByTr"
        response = self._request("GET", url, params={"trId": tr_id})
        response.raise_for_status()
        return response.json()

    def get_tr_relative_feature(self, tr_id: int, pbi: str) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/feature_interaction/relativeTrFeature"
        response = self._request("GET", url, params={"trId": tr_id, "pbi": pbi})
        response.raise_for_status()
        return response.json()

    def get_tr_relative_ir(self, tr_id: int) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/tr/relativeIr"
        response = self._request("GET", url, params={"trId": tr_id})
        response.raise_for_status()
        return response.json()

    def get_cida_config(self, pbi: int) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/config/{pbi}/cida_config"
        response = self._request("GET", url)
        response.raise_for_status()
        return response.json()

    def get_design_task_info_tree(self, pbi: int, owner_id: str) -> dict[str, Any]:
        url = f"{BASE_URL}{API_V2}/test_design_tree/{pbi}/design_task_info_tree"
        response = self._request("GET", url, params={"ownerId": owner_id})
        response.raise_for_status()
        return response.json()

    # ---- create_tr ----
    def get_ir_infos(self, design_task_id: int) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/requirement/irInfos"
        response = self._request("GET", url, params={"designTaskId": design_task_id})
        response.raise_for_status()
        return response.json()

    def get_sr_infos(self, design_task_id: int) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/requirement/srInfos"
        response = self._request("GET", url, params={"designTaskId": design_task_id})
        response.raise_for_status()
        return response.json()

    def verify_tr_name(self, design_task_id: int, tr_name: str) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/tr/trVerify"
        response = self._request("GET", url, params={"designTaskId": design_task_id, "trName": tr_name})
        response.raise_for_status()
        return response.json()

    def create_tr(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/tr"
        response = self._request("POST", url, json=payload)
        response.raise_for_status()
        return response.json()

    def check_create_activity_by_doc_id(self, creator: str, idp_doc_id: str) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/permissions/{creator}/check_create_activity_by_doc_id"
        response = self._request("GET", url, params={"idpDocId": idp_doc_id})
        response.raise_for_status()
        return response.json()

    def get_tr_children(self, tr_id: int, user_id: str) -> dict[str, Any]:
        url = f"{BASE_URL}{API_V2}/test_design_tree/{tr_id}/tr_children"
        response = self._request("GET", url, params={"user_id": user_id, "_": "1782266050984"})
        response.raise_for_status()
        return response.json()

    def get_single_ts(self, ts_id: int) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/ts/singleTs"
        response = self._request("GET", url, params={"tsId": ts_id})
        response.raise_for_status()
        return response.json()

    # ---- create_ts ----
    def get_design_task(self, design_task_id: int) -> dict[str, Any]:
        url = f"{BASE_URL}{API_V2}/design_task/{design_task_id}/singleDesignTask"
        response = self._request("GET", url)
        response.raise_for_status()
        return response.json()

    def get_tr_info(self, tr_id: int) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/tr/{tr_id}/singleTr"
        response = self._request("GET", url)
        response.raise_for_status()
        return response.json()

    def verify_ts_name(self, tr_id: int, ts_name: str) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/ts/create_ts_verify"
        response = self._request("GET", url, params={"tr_id": tr_id, "ts_name": ts_name})
        response.raise_for_status()
        return response.json()

    def create_ts(self, payload: dict[str, Any], parent_tr_id: int) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/ts/create"
        response = self._request("POST", url, json=payload, params={"parentTrId": parent_tr_id})
        response.raise_for_status()
        return response.json()

    def get_relative_ir(self, tr_id: int) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/requirement/relativeTrRequirement"
        response = self._request("GET", url, params={"trId": tr_id})
        response.raise_for_status()
        return response.json()

    def query_tr_relate_scene(self, tr_id: int, asso_act_type_list: list[str]) -> dict[str, Any]:
        url = f"{BASE_URL}{API_V2}/scene_analysis/tr_relate_scene/query"
        payload = {"trId": str(tr_id), "assoActTypeList": asso_act_type_list}
        response = self._request("POST", url, json=payload)
        response.raise_for_status()
        return response.json()

    def query_tr_relate_function(self, tr_id: int, asso_act_type_list: list[str]) -> dict[str, Any]:
        url = f"{BASE_URL}{API_V2}/function_analysis/tr_relate_function/{tr_id}"
        response = self._request("POST", url, json=asso_act_type_list)
        response.raise_for_status()
        return response.json()

    def query_tr_relate_feature(self, tr_id: int, feature_tree_type: str = "fullDesignFeatureTree") -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/feature_interaction/feature"
        response = self._request("GET", url, params={"featureTreeType": feature_tree_type, "trId": tr_id})
        response.raise_for_status()
        return response.json()

    # ---- create_tp ----
    def verify_tp_name(self, ts_id: int, tp_name: str) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/tp/tpVerify"
        response = self._request("GET", url, params={"tsId": ts_id, "tpName": tp_name})
        response.raise_for_status()
        return response.json()

    def create_tp(self, pbi: str, ts_id: int, tp_type: str, tp_source_type: str, parent_tr_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/tp/create"
        response = self._request("POST", url, json=payload, params={
            "pbi": pbi, "tsId": ts_id, "tpType": tp_type,
            "tpSourceType": tp_source_type, "parentTrId": parent_tr_id,
        })
        response.raise_for_status()
        return response.json()

    def get_relative_ts_requirement(self, ts_id: int) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/requirement/relativeTsRequirement"
        response = self._request("GET", url, params={"tsId": ts_id})
        response.raise_for_status()
        return response.json()

    def query_scene_factor(self, ts_id: int, version_pbi: str, asso_act_type_list: list[str] | None = None, source_type_list: list[str] | None = None) -> dict[str, Any]:
        url = f"{BASE_URL}{API_V2}/scene_factory_analysis/ts_relate_scene_factor/query"
        payload: dict[str, Any] = {"tsId": str(ts_id), "versionPbi": version_pbi}
        if asso_act_type_list:
            payload["assoActTypeList"] = asso_act_type_list
        if source_type_list:
            payload["sourceTypeList"] = source_type_list
        response = self._request("POST", url, json=payload)
        response.raise_for_status()
        return response.json()

    def query_test_factor(self, activity_id: int, asso_act_type_list: list[str] | None = None, factor_type: str | None = None) -> dict[str, Any]:
        url = f"{BASE_URL}{API_V2}/factor_analysis/ts_factor_relate_info"
        payload: dict[str, Any] = {"activityId": str(activity_id)}
        if asso_act_type_list:
            payload["assoActTypeList"] = asso_act_type_list
        if factor_type:
            payload["type"] = factor_type
        response = self._request("POST", url, json=payload)
        response.raise_for_status()
        return response.json()

    # ---- create_tc ----
    def query_ts_factor_relate_info(self, activity_id: int, asso_act_type_list: list[str], factor_type: str) -> dict[str, Any]:
        url = f"{BASE_URL}{API_V2}/factor_analysis/ts_factor_relate_info"
        payload = {"activityId": str(activity_id), "assoActTypeList": asso_act_type_list, "type": factor_type}
        response = self._request("POST", url, json=payload)
        response.raise_for_status()
        return response.json()

    def create_tc(self, payload: dict[str, Any], tp_id: int) -> dict[str, Any]:
        url = f"{BASE_URL}/test_design/api/v1/tc_info/createTc"
        response = self._request("POST", url, json=payload, params={"tpId": tp_id})
        response.raise_for_status()
        return response.json()


_client = TestDesignClient()


def get_client() -> TestDesignClient:
    return _client


def _parse_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def validate_required_params(**kwargs) -> dict[str, Any] | None:
    for param_name, param_value in kwargs.items():
        if param_value is None or param_value == "":
            return {"success": False, "error": f"参数 {param_name} 是必填参数"}
    return None


def add_extra_fields(item: dict[str, Any], item_type: str) -> dict[str, Any]:
    source_type_name_map = {"function": "需求分析引入", "feature": "设计同源引入"}
    item["sourceTypeName"] = source_type_name_map.get(item_type, "")
    item["statusName"] = "工作中"
    item["tiDisabled"] = False
    return item


def build_factor_item(factor: dict[str, Any], creator: str) -> dict[str, Any]:
    source_type_name_map = {"TsTestCustomization": "测试自定义"}
    factor_type_name_map = {"1": "Data", "0": "Action"}
    factor_type = str(factor.get("type", factor.get("customType", "")))
    is_data_factor = factor_type == "1"
    item = {
        "creator": factor.get("creator", creator),
        "createTime": factor.get("createTime"),
        "modifier": factor.get("modifier"),
        "updateTime": factor.get("updateTime"),
        "deleted": factor.get("deleted", 0),
        "keyId": str(factor.get("customTestFactorId", "")),
        "name": factor.get("name"),
        "description": factor.get("description"),
        "factorType": factor_type,
        "sourceType": factor.get("sourceType"),
        "source": factor.get("source"),
        "sequence": factor.get("sequence", 0),
        "number": factor.get("number"),
        "pbi": factor.get("pbi"),
        "status": factor.get("status"),
        "customTestFactorId": factor.get("customTestFactorId"),
        "customTestFactorCode": factor.get("customTestFactorCode"),
        "customType": factor.get("customType"),
        "realNumber": factor.get("number"),
        "testOrScene": "testFactor",
        "factorTypeCh": factor_type_name_map.get(factor_type, ""),
        "sourceTypeCh": source_type_name_map.get(factor.get("sourceType", ""), ""),
        "tiDisabled": False,
    }
    if is_data_factor:
        item.update({
            "dataType": factor.get("dataType"),
            "validValue": factor.get("validValue"),
            "invalidValue": factor.get("invalidValue"),
            "variableName": factor.get("variableName"),
        })
    else:
        item.update({
            "precondition": factor.get("precondition"),
            "factorOperationDesc": factor.get("factorOperationDesc"),
            "expectedResultDesc": factor.get("expectedResultDesc"),
            "logicDescription": factor.get("logicDescription"),
            "operation": factor.get("operation"),
            "caseDescInfo": factor.get("caseDescInfo"),
            "tcId": factor.get("tcId"),
        })
    return item


def build_scene_factor_item(scene: dict[str, Any], creator: str) -> dict[str, Any]:
    source_type_name_map = {"TsTestCustomization": "测试自定义"}
    return {
        "creator": scene.get("creator", creator),
        "createTime": scene.get("createTime"),
        "modifier": scene.get("modifier"),
        "updateTime": scene.get("updateTime"),
        "deleted": scene.get("deleted", 0),
        "id": scene.get("id"),
        "tsId": scene.get("tsId"),
        "sceneFactorCode": scene.get("sceneFactorCode"),
        "factorCustomCode": scene.get("factorCustomCode"),
        "customSceneFactorId": scene.get("customSceneFactorId"),
        "customSceneFactorCode": scene.get("customSceneFactorCode"),
        "customType": scene.get("customType"),
        "assoActType": scene.get("assoActType"),
        "sourceType": scene.get("sourceType"),
        "used": scene.get("used", False),
        "factorCode": scene.get("factorCode"),
        "factorName": scene.get("factorName"),
        "factorDesc": scene.get("factorDesc"),
        "factorDataType": scene.get("factorDataType"),
        "variableName": scene.get("variableName"),
        "dataValidValue": scene.get("dataValidValue"),
        "dataInvalidValue": scene.get("dataInvalidValue"),
        "factorStatus": scene.get("factorStatus"),
        "remark": scene.get("remark"),
        "pbi": scene.get("pbi"),
        "parentCode": scene.get("parentCode"),
        "logicDescription": scene.get("logicDescription"),
        "operationDescription": scene.get("operationDescription"),
        "precondition": scene.get("precondition"),
        "expectedResult": scene.get("expectedResult"),
        "sourceTypeCh": source_type_name_map.get(scene.get("sourceType", ""), ""),
        "tiDisabled": False,
    }


def build_test_factor_item(test_factor: dict[str, Any], creator: str) -> dict[str, Any]:
    source_type_name_map = {"TsTestCustomization": "测试自定义"}
    type_name_map = {1: "Data", 2: "Rules"}
    return {
        "creator": test_factor.get("creator", creator),
        "createTime": test_factor.get("createTime"),
        "modifier": test_factor.get("modifier"),
        "updateTime": test_factor.get("updateTime"),
        "deleted": test_factor.get("deleted", 0),
        "id": test_factor.get("id"),
        "assoActType": test_factor.get("assoActType"),
        "sourceType": test_factor.get("sourceType"),
        "testFactorId": test_factor.get("testFactorId"),
        "customTestFactorId": test_factor.get("customTestFactorId"),
        "customTestFactorCode": test_factor.get("customTestFactorCode"),
        "customType": test_factor.get("customType"),
        "name": test_factor.get("name"),
        "number": test_factor.get("number"),
        "description": test_factor.get("description"),
        "type": test_factor.get("type"),
        "pbi": test_factor.get("pbi"),
        "status": test_factor.get("status"),
        "validValues": test_factor.get("validValues"),
        "invalidValues": test_factor.get("invalidValues"),
        "variableName": test_factor.get("variableName"),
        "variableType": test_factor.get("variableType"),
        "logicDescription": test_factor.get("logicDescription"),
        "operation": test_factor.get("operation"),
        "precondition": test_factor.get("precondition"),
        "expectedResult": test_factor.get("expectedResult"),
        "modeNumber": test_factor.get("modeNumber"),
        "designSpecificationNumber": test_factor.get("designSpecificationNumber"),
        "source": test_factor.get("source"),
        "temporary": test_factor.get("temporary", 0),
        "realNumber": test_factor.get("realNumber"),
        "tsId": test_factor.get("tsId"),
        "used": test_factor.get("used", False),
        "typeCh": type_name_map.get(test_factor.get("type", 1), "Data"),
        "sourceTypeCh": source_type_name_map.get(test_factor.get("sourceType", ""), ""),
        "temporaryCh": "是" if test_factor.get("temporary") else "否",
        "tpAssociation": "未关联",
        "tiDisabled": False,
    }


def build_scene_item(scene: dict[str, Any], creator: str) -> dict[str, Any]:
    source_type_name_map = {"TrTestCustomization": "测试自定义"}
    status_name_map = {"draft": "草稿"}
    actor_info = scene.get("actorInfo")
    action_info = scene.get("actionInfo")
    return {
        "creator": scene.get("creator", creator),
        "createTime": scene.get("createTime"),
        "modifier": scene.get("modifier"),
        "updateTime": scene.get("updateTime"),
        "deleted": scene.get("deleted", 0),
        "id": scene.get("id"),
        "trId": scene.get("trId"),
        "assoActType": scene.get("assoActType"),
        "sourceType": scene.get("sourceType"),
        "almCode": scene.get("almCode"),
        "customSceneId": scene.get("customSceneId"),
        "almId": scene.get("almId"),
        "name": scene.get("name"),
        "keyId": scene.get("keyId"),
        "status": scene.get("status"),
        "involved": scene.get("involved", "1"),
        "notInvolvedReason": scene.get("notInvolvedReason"),
        "pbi": scene.get("pbi"),
        "actorId": scene.get("actorId"),
        "description": scene.get("description"),
        "actorName": scene.get("actorName"),
        "actionId": scene.get("actionId"),
        "actionName": scene.get("actionName"),
        "parentId": scene.get("parentId"),
        "used": scene.get("used", False),
        "trName": scene.get("trName"),
        "sceneName": scene.get("sceneName"),
        "actor": scene.get("actor"),
        "action": scene.get("action"),
        "actorInfo": actor_info if actor_info else {"name": scene.get("actor", "")},
        "actionInfo": action_info if action_info else {"name": scene.get("action", "")},
        "isPush": "未推送",
        "sourceTypeName": source_type_name_map.get(scene.get("sourceType", ""), ""),
        "statusName": status_name_map.get(scene.get("status", ""), ""),
        "tiDisabled": False,
    }


def build_function_item(func: dict[str, Any], creator: str) -> dict[str, Any]:
    source_type_name_map = {
        "RequirementAnalysisFunction": "需求分析引入",
        "TRFunctionInteractionAnalysis": "功能交互分析",
        "TrTestCustomization": "测试自定义",
    }
    status_name_map = {"Inwork": "工作中", "Draft": "草稿", "Released": "已发布"}
    return {
        "creator": func.get("creator", creator),
        "createTime": func.get("createTime"),
        "modifier": func.get("modifier"),
        "updateTime": func.get("updateTime"),
        "deleted": func.get("deleted", 0),
        "id": func.get("id"),
        "assoActType": func.get("assoActType"),
        "sourceType": func.get("sourceType"),
        "customFunctionId": func.get("customFunctionId", 0),
        "almCode": func.get("almCode"),
        "almId": func.get("almId"),
        "name": func.get("name"),
        "keyId": func.get("keyId"),
        "status": func.get("status"),
        "involved": func.get("involved"),
        "notInvolvedReason": func.get("notInvolvedReason"),
        "path": func.get("path"),
        "category": func.get("category"),
        "description": func.get("description"),
        "input": func.get("input"),
        "process": func.get("process"),
        "output": func.get("output"),
        "functionConstraint": func.get("functionConstraint"),
        "resModifier": func.get("resModifier"),
        "resUpdateTime": func.get("resUpdateTime"),
        "pbi": func.get("pbi"),
        "functionDomainId": func.get("functionDomainId"),
        "trId": func.get("trId"),
        "used": func.get("used", False),
        "statusCh": status_name_map.get(func.get("status", ""), ""),
        "sourceTypeCh": source_type_name_map.get(func.get("sourceType", ""), ""),
        "tiDisabled": False,
    }


def build_feature_item(feature: dict[str, Any], creator: str) -> dict[str, Any]:
    source_type_name_map = {"RequirementIntroduction": "设计同源引入"}
    status_name_map = {"Inwork": "工作中"}
    return {
        "creator": feature.get("creator", creator),
        "createTime": feature.get("createTime"),
        "modifier": feature.get("modifier"),
        "updateTime": feature.get("updateTime"),
        "deleted": feature.get("deleted", 0),
        "id": feature.get("id"),
        "trId": feature.get("trId"),
        "almId": feature.get("almId"),
        "almCode": feature.get("almCode"),
        "name": feature.get("name"),
        "category": feature.get("category"),
        "status": feature.get("status"),
        "tsId": feature.get("tsId"),
        "tsType": feature.get("tsType"),
        "tsName": feature.get("tsName"),
        "description": feature.get("description"),
        "resolveDescription": feature.get("resolveDescription"),
        "assoActType": feature.get("assoActType"),
        "sourceType": feature.get("sourceType"),
        "pbi": feature.get("pbi"),
        "featureTreeType": feature.get("featureTreeType"),
        "used": feature.get("used", False),
        "sourceTypeName": source_type_name_map.get(feature.get("sourceType", ""), ""),
        "statusName": status_name_map.get(feature.get("status", ""), ""),
        "tiDisabled": False,
    }


@mcp.tool(name="get_design_task_info_init")
def get_design_task_info_init_tool(
    product_name: str,
    owner_id: str,
) -> dict[str, Any]:
    """获取设计任务信息（IR嵌套SR分组结构）

    Args:
        product_name: 产品名称，如 "UPCF 27.0.0"
        owner_id: 负责人ID（工号）

    Returns:
        设计任务信息列表，IR下嵌套SR，特性和功能与IR同级
    """
    try:
        client = get_client()
        # 先根据产品名称获取PBI ID
        pbi_result = client.get_pbi_id(product_name)
        pbi = pbi_result.get("id")
        if not pbi:
            return {"success": False, "error": f"未找到产品 '{product_name}' 对应的PBI ID"}

        result = client.get_design_task_info_tree(int(pbi), owner_id)

        if not result.get("meta", {}).get("isSuccess", True):
            return {
                "success": False,
                "error": result.get("meta", {}).get("message", "获取设计任务信息失败"),
            }

        # 获取projectId
        cida_result = client.get_cida_config(int(pbi))
        project_id = None
        cida_data = cida_result.get("data", [])
        if cida_data and len(cida_data) > 0:
            project_id = cida_data[0].get("projectId")

        data = result.get("data", [])
        task_list = []
        for item in data:
            if item.get("nodeType") != "DesignTask":
                continue
            design_task_id = item.get("resourceId")
            task_info = {
                "design_task_id": design_task_id,
                "name": item.get("name"),
                "idp_doc_id": item.get("idpDocId"),
            }

            # 获取需求分析信息
            try:
                req_result = client.get_requirement_infos(design_task_id)
                requirements = req_result.get("data", [])

                # 按 requirementParentId 分组：null 为 IR，有值为 SR
                ir_list = []
                sr_map = {}  # key: IR的requirementAlmId, value: SR列表
                for r in requirements:
                    if r.get("requirementParentId") is None or r.get("requirementParentId") == '' or r.get("requirementParentId") == '0':
                        ir_list.append(r)
                    else:
                        parent_id = r.get("requirementParentId")
                        sr_map.setdefault(parent_id, []).append(r)

                # 构建 IR 嵌套 SR 的结构
                ir_infos = []
                for ir in ir_list:
                    alm_id = ir.get("requirementAlmId")
                    sr_infos = [{
                        "requirement_id": sr.get("requirementId"),
                        "requirement_name": sr.get("requirementName"),
                        "requirement_type": sr.get("requirementType"),
                        "requirementParentId": sr.get("requirementParentId"),
                        "assoActType": sr.get("assoActType"),
                    } for sr in sr_map.get(alm_id, [])]

                    ir_infos.append({
                        "requirement_id": ir.get("requirementId"),
                        "requirement_name": ir.get("requirementName"),
                        "requirement_type": ir.get("requirementType"),
                        "requirementAlmId": ir.get("requirementAlmId"),
                        "assoActType": ir.get("assoActType"),
                        "sr_list": sr_infos,
                    })

                feature_result = client.get_feature_infos(design_task_id)
                function_result = client.get_function_infos(design_task_id)
                tr_result = client.get_tr_infos(design_task_id)

                feature_infos = [{
                    "feature_id": f.get("featureId"),
                    "feature_number": f.get("featureNumber"),
                    "feature_name": f.get("featureName"),
                    "feature_category": f.get("featureCategory"),
                    "description": f.get("description"),
                    "requirement_id": f.get("requirementId"),
                    "assoActType": f.get("assoActType"),
                    "requirement_number": f.get("requirementNumber"),
                } for f in feature_result.get("data", [])]

                function_infos = [{
                    "function_id": fn.get("functionId"),
                    "function_number": fn.get("functionNumber"),
                    "function_name": fn.get("functionName"),
                    "function_description": fn.get("functionDescription"),
                    "requirement_id": fn.get("requirementId"),
                    "requirement_number": fn.get("requirementNumber"),
                    "key_id": fn.get("keyId"),
                    "function_status": fn.get("functionStatus"),
                    "function_process": fn.get("functionProcess"),
                    "function_path": fn.get("functionPath"),
                    "function_input": fn.get("functionInput"),
                    "function_output": fn.get("functionOutput"),
                    "function_constraint": fn.get("functionConstraint"),
                    "assoActType": fn.get("assoActType"),
                } for fn in function_result.get("data", [])]

                tr_infos = []
                for tr in tr_result.get("data", []):
                    tr_id = tr.get("id")
                    tr_pbi = tr.get("pbi")
                    tr_item = {
                        "tr_id": tr_id,
                        "tr_name": tr.get("trName"),
                        "tr_no": tr.get("trNo"),
                        "description": tr.get("description"),
                        "resolve_description": tr.get("resolveDescription"),
                        "status": tr.get("status"),
                        "pbi": tr_pbi,
                        "creator": tr.get("creator"),
                        "create_time": tr.get("createTime"),
                        "relation_function": tr.get("relationFunction"),
                        "relation_function_name": tr.get("relationFunctionName"),
                        "relation_feature": tr.get("relationFeature"),
                        "relation_feature_name": tr.get("relationFeatureName"),
                        "relation_requirement": tr.get("relationRequirement"),
                        "relation_requirement_name": tr.get("relationRequirementName"),
                        "tr_resource_type": tr.get("trResourceType"),
                    }
                    # 调用4个关联接口获取TR的关联信息
                    try:
                        scene_result = client.get_tr_relative_scene(tr_id)
                        tr_item["scene_list"] = [{
                            "id": s.get("id"),
                            "name": s.get("name"),
                            "alm_code": s.get("almCode"),
                            "key_id": s.get("keyId"),
                            "status": s.get("status"),
                            "source_type": s.get("sourceType"),
                        } for s in scene_result.get("data", [])]
                    except Exception:
                        tr_item["scene_list"] = []

                    try:
                        func_result = client.get_tr_relative_function(tr_id)
                        tr_item["function_list"] = [{
                            "id": f.get("id"),
                            "name": f.get("name"),
                            "alm_code": f.get("almCode"),
                            "key_id": f.get("keyId"),
                            "status": f.get("status"),
                            "category": f.get("category"),
                            "description": f.get("description"),
                        } for f in func_result.get("data", [])]
                    except Exception:
                        tr_item["function_list"] = []

                    try:
                        feat_result = client.get_tr_relative_feature(tr_id, tr_pbi)
                        tr_item["feature_list"] = [{
                            "id": f.get("id"),
                            "name": f.get("name"),
                            "alm_id": f.get("almId"),
                            "requirement_name": f.get("requirementName"),
                        } for f in feat_result.get("data", [])]
                    except Exception:
                        tr_item["feature_list"] = []

                    try:
                        ir_result = client.get_tr_relative_ir(tr_id)
                        tr_item["ir_list"] = [{
                            "id": r.get("id"),
                            "requirement_alm_id": r.get("requirementAlmId"),
                            "requirement_name": r.get("requirementName"),
                            "requirement_type": r.get("requirementType"),
                        } for r in ir_result.get("data", [])]
                    except Exception:
                        tr_item["ir_list"] = []

                    tr_infos.append(tr_item)

                task_info["ir_list"] = ir_infos
                task_info["feature_list"] = feature_infos
                task_info["function_list"] = function_infos
                task_info["tr_list"] = tr_infos
            except Exception as e:
                print(f"获取需求分析信息失败(design_task_id={design_task_id}): {str(e)}")
                task_info["ir_list"] = None
                task_info["feature_list"] = None
                task_info["function_list"] = None
                task_info["tr_list"] = None

            task_list.append(task_info)
        return {
            "success": True,
            "pbi": int(pbi),
            "project_id": project_id,
            "data": task_list,
        }
    except Exception as e:
        print(f"获取设计任务信息失败: {str(e)}")
        return {"success": False, "error": str(e)}


@mcp.tool(name="create_tr")
def create_tr_tool(
    pbi: int,
    task_name: str,
    tr_name: str,
    description: str,
    resolve_description: str,
    creator: str,
    requirement_ids: str | None = None,
    function_numbers: str | None = None,
    feature_numbers: str | None = None,
) -> dict[str, Any]:
    """创建TR（测试需求）

    Args:
        pbi: PBI编号
        task_name: 设计任务名称
        tr_name: TR名称
        description: TR描述
        resolve_description: 分解逻辑说明
        creator: 创建人工号
        requirement_ids: 需求ID列表，逗号分隔（如"SR001,SR002"）
        function_numbers: 功能编号列表，逗号分隔（传入则走SR/功能列表类型）
        feature_numbers: 特性编号列表，逗号分隔（传入则走IR/特性列表类型）

    Returns:
        创建结果
    """
    try:
        error = validate_required_params(
            pbi=pbi, task_name=task_name, tr_name=tr_name,
            description=description, resolve_description=resolve_description,
            creator=creator, requirement_ids=requirement_ids,
        )
        if error:
            return error
        client = get_client()
        req_ids: list[str] = _parse_list(requirement_ids)
        func_nums: list[str] = _parse_list(function_numbers)
        feat_nums: list[str] = _parse_list(feature_numbers)

        tree_result = client.get_design_task_info_tree(pbi, creator)
        if not tree_result.get("meta", {}).get("isSuccess", True):
            return {"success": False, "error": tree_result.get("meta", {}).get("message", "获取设计任务信息失败")}

        task_nodes = [node for node in tree_result.get("data", []) if node.get("name") == task_name]
        if not task_nodes:
            return {"success": False, "error": f"未找到名称为 {task_name} 的设计任务"}

        task_info = task_nodes[0]
        pbi_version_id = str(task_info.get("pbi", ""))
        idp_doc_id = task_info.get("idpDocId", "")
        design_task_id = task_info.get("resourceId", "")

        verify_result = client.verify_tr_name(design_task_id, tr_name)
        if not verify_result.get("meta", {}).get("isSuccess", False):
            return {"success": False, "error": f"TR名称 '{tr_name}' 已存在，请使用其他名称"}

        check_result = client.check_create_activity_by_doc_id(creator, idp_doc_id)
        if not check_result.get("success", False):
            return {"success": False, "error": check_result.get("meta", {}).get("message", "当前文档未绑定测试设计任务")}

        if func_nums:
            sr_infos = client.get_sr_infos(design_task_id)
            function_infos = client.get_function_infos(design_task_id)
            selected_requirements = [req for req in sr_infos.get("data", []) if req.get("requirementId") in req_ids]
            selected_functions = [add_extra_fields(func, "function") for func in function_infos.get("data", []) if func.get("functionNumber") in func_nums]
            payload = {
                "designTaskId": str(design_task_id), "trName": tr_name, "description": description,
                "resolveDescription": resolve_description, "creator": creator,
                "requirementIds": [int(req["requirementAlmId"]) for req in selected_requirements],
                "functionInfoList": selected_functions, "featureInfoList": [],
                "pbiVersionId": pbi_version_id, "idpDocId": idp_doc_id, "trResourceType": "srAndFunction",
            }
        elif feat_nums:
            ir_infos = client.get_ir_infos(design_task_id)
            feature_infos = client.get_feature_infos(design_task_id)
            selected_irs = [ir for ir in ir_infos.get("data", []) if ir.get("requirementId") in req_ids]
            selected_features = [add_extra_fields(feat, "feature") for feat in feature_infos.get("data", []) if feat.get("featureNumber") in feat_nums]
            payload = {
                "designTaskId": str(design_task_id), "trName": tr_name, "description": description,
                "resolveDescription": resolve_description, "creator": creator,
                "requirementIds": [int(ir["requirementAlmId"]) for ir in selected_irs],
                "functionInfoList": [], "featureInfoList": selected_features,
                "pbiVersionId": pbi_version_id, "idpDocId": idp_doc_id, "trResourceType": "irAndFeature",
            }
        else:
            return {"success": False, "error": "必须提供 function_numbers 或 feature_numbers 之一"}

        result = client.create_tr(payload)
        if result.get("meta", {}).get("isSuccess", True):
            tr_id = result.get("data", 0)
            print(f"创建TR成功, designTaskId={pbi}, trName={tr_name}, trId={tr_id}")
            if tr_id is None:
                return {
                "success": True,
                "data": {
                    "tr_name": tr_name,
                    "design_task_id": design_task_id
                },
            }
            children_result = client.get_tr_children(tr_id, creator)
            ts_list = []
            if children_result.get("meta", {}).get("isSuccess", True):
                ts_nodes = [node for node in children_result.get("data", []) if node.get("nodeType") == "TS"]
                for ts_node in ts_nodes:
                    resource_id = ts_node.get("resourceId")
                    if not resource_id:
                        continue
                    ts_result = client.get_single_ts(resource_id)
                    if not ts_result.get("meta", {}).get("isSuccess", True):
                        continue
                    ts_data = ts_result.get("data", {})
                    ts_list.append({"ts_name": ts_data.get("tsName", ""), "ts_type": ts_data.get("tsType", ""), "ts_id": ts_data.get("id", 0)})
            return {"success": True, "data": {"tr_id": tr_id, "tr_name": tr_name, "ts_list": ts_list, "design_task_id": design_task_id}}
        else:
            return {"success": False, "error": result.get("meta", {}).get("message", "创建TR失败")}
    except Exception as e:
        print(f"创建TR失败: {str(e)}")
        return {"success": False, "error": str(e)}


@mcp.tool(name="create_ts")
def create_ts_tool(
    designTaskId: int,
    trId: int,
    tsName: str,
    tsType: str,
    creator: str,
    description: str = "",
    resolveDescription: str = "",
    sceneSelecteds: str | None = None,
    functionSelecteds: str | None = None,
    featureSelecteds: str | None = None,
    requirement_ids: str | None = None,
) -> dict[str, Any]:
    """创建TS（测试场景）

    Args:
        designTaskId: 设计任务ID
        trId: 所属TR的ID
        tsName: TS名称
        tsType: TS类型 (scene/function/feature/constraint)
        creator: 创建人工号
        description: TS描述
        resolveDescription: 分解逻辑说明
        sceneSelecteds: 关联的场景名称列表，逗号分隔
        functionSelecteds: 关联的功能名称列表，逗号分隔
        featureSelecteds: 关联的特性名称列表，逗号分隔
        requirement_ids: 需求ID列表，逗号分隔

    Returns:
        创建结果
    """
    try:
        error = validate_required_params(
            designTaskId=designTaskId, trId=trId, tsName=tsName,
            tsType=tsType, creator=creator,
        )
        if error:
            return error
        client = get_client()
        scene_name_list: list[str] = _parse_list(sceneSelecteds)
        function_name_list: list[str] = _parse_list(functionSelecteds)
        feature_id_list: list[str] = _parse_list(featureSelecteds)
        req_id_list: list[str] = _parse_list(requirement_ids)

        design_task_info = client.get_design_task(designTaskId)
        pbi = str(design_task_info.get("data", {}).get("pbi", ""))
        idp_doc_id = design_task_info.get("data", {}).get("idpDocId", "")

        verify_result = client.verify_ts_name(trId, tsName)
        if not verify_result.get("meta", {}).get("isSuccess", True):
            return {"success": False, "error": f"TS名称 '{tsName}' 已存在，请使用其他名称"}

        tr_association_req_alm_id_list: list[str] = []
        if req_id_list:
            relative_ir_result = client.get_relative_ir(trId)
            if relative_ir_result and relative_ir_result.get("data") is not None:
                tr_association_req_alm_id_list = [
                    item["requirementAlmId"] for item in relative_ir_result.get("data", [])
                    if item.get("requirementId") in req_id_list
                ]

        scene_selected_list: list[dict[str, Any]] = []
        if scene_name_list:
            scene_result = client.query_tr_relate_scene(trId, ["RequirementAnalysis", "SceneAnalysis"])
            scene_map = {scene.get("name", ""): scene for scene in scene_result.get("data", [])}
            for scene_name in scene_name_list:
                scene_data = scene_map.get(scene_name)
                if scene_data:
                    scene_selected_list.append(build_scene_item(scene_data, creator))

        function_selected_list: list[dict[str, Any]] = []
        if function_name_list:
            func_result = client.query_tr_relate_function(trId, ["RequirementAnalysis", "TRFunctionInteractionAnalysis", "TrTestCustomization"])
            func_map = {func.get("name", ""): func for func in func_result.get("data", [])}
            for func_name in function_name_list:
                func_data = func_map.get(func_name)
                if func_data:
                    function_selected_list.append(build_function_item(func_data, creator))

        feature_selected_list: list[dict[str, Any]] = []
        if feature_id_list:
            feature_result = client.query_tr_relate_feature(trId)
            feature_map = {feat.get("name", ""): feat for feat in feature_result.get("data", [])}
            for feat_name in feature_id_list:
                feat_data = feature_map.get(feat_name)
                if feat_data:
                    feature_selected_list.append(build_feature_item(feat_data, creator))

        payload = {
            "trId": str(trId), "tsType": tsType, "tsName": tsName,
            "description": description, "resolveDescription": resolveDescription,
            "sceneSelectedList": scene_selected_list, "creator": creator,
            "status": "新建", "pbi": pbi, "idpDocId": idp_doc_id,
            "trAssociationRequirementAlmIdList": tr_association_req_alm_id_list,
            "functionSelectedList": function_selected_list,
            "featureSelectedList": feature_selected_list,
        }

        result = client.create_ts(payload, trId)
        if result.get("meta", {}).get("isSuccess", True):
            ts_id = result.get("data", 0)
            print(f"创建TS成功, designTaskId={designTaskId}, trId={trId}, tsName={tsName}, tsId={ts_id}")
            return {"success": True, "data": {"tsId": ts_id, "tsName": tsName}}
        else:
            return {"success": False, "error": result.get("meta", {}).get("message", "创建TS失败")}
    except Exception as e:
        print(f"创建TS失败: {str(e)}")
        return {"success": False, "error": str(e)}


@mcp.tool(name="create_tp")
def create_tp_tool(
    designTaskId: int,
    tsId: int,
    parentTrId: int,
    tpType: str,
    tpSourceType: str,
    tpName: str,
    creator: str,
    description: str = "",
    resolveDescription: str = "",
    sceneFactorNames: str | None = None,
    testFactorNames: str | None = None,
    requirement_ids: str | None = None,
) -> dict[str, Any]:
    """创建TP（测试点）

    Args:
        designTaskId: 设计任务ID
        tsId: 所属TS的ID
        parentTrId: 父TR的ID
        tpType: TP类型
        tpSourceType: TP资源类型
        tpName: TP名称
        creator: 创建人工号
        description: TP描述
        resolveDescription: 分解逻辑说明
        sceneFactorNames: 场景因子名称列表，逗号分隔
        testFactorNames: 测试因子名称列表，逗号分隔
        requirement_ids: 需求ID列表，逗号分隔

    Returns:
        创建结果
    """
    try:
        error = validate_required_params(
            designTaskId=designTaskId, tsId=tsId, parentTrId=parentTrId,
            tpType=tpType, tpSourceType=tpSourceType, tpName=tpName, creator=creator,
        )
        if error:
            return error
        client = get_client()
        scene_factor_name_list: list[str] = _parse_list(sceneFactorNames)
        test_factor_name_list: list[str] = _parse_list(testFactorNames)
        req_id_list: list[str] = _parse_list(requirement_ids)

        design_task_info = client.get_design_task(designTaskId)
        pbi = str(design_task_info.get("data", {}).get("pbi", ""))
        idp_doc_id = design_task_info.get("data", {}).get("idpDocId", "")

        verify_result = client.verify_tp_name(tsId, tpName)
        if not verify_result.get("meta", {}).get("isSuccess", True):
            return {"success": False, "error": f"TP名称 '{tpName}' 已存在，请使用其他名称"}

        scene_factor_list: list[dict[str, Any]] = []
        if scene_factor_name_list:
            scene_result = client.query_scene_factor(
                ts_id=tsId, version_pbi=pbi,
                asso_act_type_list=["BusinessSceneAnalysis", "SceneAnalysis", "RequirementAnalysis"],
                source_type_list=["SceneFactorLibrary", "SceneIdentificationIntroduction", "TsTestCustomization", "RequirementIntroduction"],
            )
            scene_map = {scene.get("factorName", ""): scene for scene in scene_result.get("data", [])}
            for scene_name in scene_factor_name_list:
                scene_data = scene_map.get(scene_name)
                if scene_data:
                    scene_factor_list.append(build_scene_factor_item(scene_data, creator))

        test_factor_list: list[dict[str, Any]] = []
        if test_factor_name_list:
            test_result = client.query_test_factor(
                activity_id=tsId,
                asso_act_type_list=["BusinessInterImplAnalysis"],
                factor_type="BusinessInterImplAnalysis",
            )
            test_map = {test_factor.get("name", ""): test_factor for test_factor in test_result.get("data", [])}
            for test_name in test_factor_name_list:
                test_data = test_map.get(test_name)
                if test_data:
                    test_factor_list.append(build_test_factor_item(test_data, creator))

        tp_association_req_alm_id_list: list[str] = []
        if req_id_list:
            relative_req_result = client.get_relative_ts_requirement(tsId)
            tp_association_req_alm_id_list = [
                item["requirementAlmId"] for item in relative_req_result.get("data", [])
                if item.get("requirementId") in req_id_list
            ]

        payload = {
            "tpName": tpName, "description": description, "resolveDescription": resolveDescription,
            "idpDocId": idp_doc_id, "creator": creator,
            "tpAssociationRequirementAlmIdList": tp_association_req_alm_id_list,
            "securityConfigIdList": [], "speiIdList": [],
        }
        if tpSourceType == "功能交互设计-功能与测试因子":
            payload["sceneFactorIdList"] = scene_factor_list
        elif tpSourceType == "测试类型交互设计—测试因子":
            payload["testFactorIdList"] = test_factor_list

        result = client.create_tp(pbi, tsId, tpType, quote(tpSourceType, safe=""), parentTrId, payload)
        if result.get("meta", {}).get("isSuccess", True):
            print(f"创建TP成功, designTaskId={designTaskId}, tsId={tsId}, tpName={tpName}")
            return {"success": True, "data": result.get("data", {})}
        else:
            return {"success": False, "error": result.get("meta", {}).get("message", "创建TP失败")}
    except Exception as e:
        print(f"创建TP失败: {str(e)}")
        return {"success": False, "error": str(e)}


@mcp.tool(name="create_tc")
def create_tc_tool(
    tp_id: int,
    name: str,
    case_id_prefix: str,
    case_id_start_value: int,
    case_id_number: str,
    auto_type: int,
    rank: str,
    description: str = "",
    preparation: str = "",
    test_step: str = "",
    expect_output: str = "",
    post_process: str = "",
    case_remark: str = "",
    owner: str = "",
    creator: str = "",
    pbi: str = "",
    test_case_type: str = "",
    test_case_activity: str = "",
    tr_id: int = 0,
    apply_version: str = "",
    test_environment_id: str = "",
    test_environment_type: str = "",
    execution_platform: str = "",
    test_case_author: str = "",
    test_case_feature: str = "",
    case_id_type: str = "input_begin",
    action_factor_names: str = "",
    data_factor_names: str = "",
    vbs_flag: str = "",
    threshold_flag: str = "",
    case_id: str = "",
) -> dict[str, Any]:
    """创建TC（测试用例）

    Args:
        tp_id: 测试计划ID
        name: 用例名称
        case_id_prefix: 用例ID前缀
        case_id_start_value: 用例ID起始值
        case_id_number: 用例编号
        auto_type: 自动化类型 (0: 手工, 1: 自动化)
        rank: 用例等级 (1/2/3/4)
        description: 用例描述
        preparation: 前置条件
        test_step: 测试步骤
        expect_output: 预期输出
        post_process: 后置处理
        case_remark: 用例备注
        owner: 负责人
        creator: 创建人
        pbi: PBI编号
        test_case_type: 用例类型
        test_case_activity: 用例活动
        tr_id: TR的ID，用于查询因子
        apply_version: 适用版本
        test_environment_id: 测试环境ID
        test_environment_type: 测试环境类型
        execution_platform: 执行平台
        test_case_author: 用例作者
        test_case_feature: 用例特性
        case_id_type: 用例ID类型 (input_begin)
        action_factor_names: 动作因子名称列表，逗号分隔
        data_factor_names: 数据因子名称列表，逗号分隔
        vbs_flag: VBS标志
        threshold_flag: 阈值标志
        case_id: 用例ID

    Returns:
        创建结果
    """
    try:
        error = validate_required_params(
            tp_id=tp_id, name=name, case_id_prefix=case_id_prefix,
            case_id_start_value=case_id_start_value, case_id_number=case_id_number,
            auto_type=auto_type, rank=rank, creator=creator,
            preparation=preparation, test_step=test_step, expect_output=expect_output,
        )
        if error:
            return error
        client = get_client()

        action_factor_info_list: list[dict[str, Any]] = []
        data_factor_info_list: list[dict[str, Any]] = []
        action_factor_name_list: list[str] = _parse_list(action_factor_names)
        data_factor_name_list: list[str] = _parse_list(data_factor_names)

        if (action_factor_name_list or data_factor_name_list) and tr_id:
            factor_result = client.query_ts_factor_relate_info(tr_id, ["BusinessInterImplAnalysis"], "BusinessInterImplAnalysis")
            factor_map = {factor.get("name", ""): factor for factor in factor_result.get("data", [])}
            all_factor_names = set(action_factor_name_list) | set(data_factor_name_list)
            for factor_name in all_factor_names:
                factor_data = factor_map.get(factor_name)
                if factor_data:
                    factor_item = build_factor_item(factor_data, creator)
                    factor_type = str(factor_data.get("type", factor_data.get("customType", "")))
                    if factor_type == "1":
                        data_factor_info_list.append(factor_item)
                    else:
                        action_factor_info_list.append(factor_item)

        payload = {
            "name": name, "caseIdPrefix": case_id_prefix, "caseIdConnSign": "_",
            "caseIdStartValue": case_id_start_value, "caseIdNumber": case_id_number,
            "autoType": auto_type, "rank": rank, "description": description,
            "preparation": preparation, "testStep": test_step, "expectOutput": expect_output,
            "postProcess": post_process, "caseRemark": case_remark, "owner": owner,
            "creator": creator, "status": "notArchived", "pbi": pbi,
            "testCaseType": test_case_type, "testCaseActivity": test_case_activity,
            "applyVersion": apply_version, "testEnvironmentId": test_environment_id,
            "testEnvironmentType": test_environment_type, "executionPlatform": execution_platform,
            "testCaseAuthor": test_case_author, "testCaseFeature": test_case_feature,
            "caseIdType": case_id_type, "actionFactorInfo": action_factor_info_list,
            "dataFactorInfo": data_factor_info_list, "vbsFlag": vbs_flag,
            "thresholdFlag": threshold_flag, "caseId": case_id,
        }

        result = client.create_tc(payload, tp_id)
        if result.get("meta", {}).get("isSuccess", True):
            tc_id = result.get("data", 0)
            return {"success": True, "data": "创建TC成功"}
        else:
            return {"success": False, "error": result.get("meta", {}).get("message", "创建TC失败")}
    except Exception as e:
        print(f"创建TC失败: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8765)
    # mcp.run()
    # print(get_design_task_info_init_tool("UNC USMF 24.0.0", "c00959281"))
    # create_tr_tool(266926538, "Nsmf/Nupf链路容灾功能补齐-5GC-UPCF", "Nsmf/Nupf链路容灾功能补齐-5GC-UPCF-1",
    #                "本TR对应需求IR20251206000098，整合该需求下全部2个SR的测试内容，组织为测试规格。",
    #                "依据需求IR20251206000098的实现设计，对其下2个SR逐项开展测试验证。",
    #                "z00655423", "SR20260124957076,SR20260124957173", "", "FEA002024032004168177")
    # create_ts_tool(
    #     designTaskId=2470,
    #     trId=3861,
    #     tsName="N7接口链路状态订阅功能验证test",
    #     tsType="function",
    #     creator="c00959281",
    #     description="验证N7接口链路状态订阅功能验证所涉及的测试内容的正确性。",
    #     resolveDescription="针对N7接口链路状态订阅功能验证设计测试，覆盖其linkInfos信元组装下发和软参控制的输入、行为与预期结果。",
    #     requirement_ids="SR20260124957076",
    #     sceneSelecteds="",
    #     functionSelecteds="",
    #     featureSelecteds=""
    # )
