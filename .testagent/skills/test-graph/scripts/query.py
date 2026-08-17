"""
testdesign 图谱查询 —— 统一入口 main(argv) -> str

命令：
  cypher    执行原始 Cypher（最灵活，一切其它能力都可用它表达）
  search    语义向量检索（任意已向量化节点，内部先 embed 再查向量索引）
  run       执行预置模板（templates/*.yaml）
  templates 列出所有预置模板
  schema    输出图谱结构（节点/字段/关系）

返回契约：
  数据命令 -> JSON 信封 {ok, action, count, data, error}，ensure_ascii=False
  -h / 参数错误 -> argparse 原生纯文本
  运行期错误 -> 信封 {ok:false, data:null, error:"..."}
  返回中绝不含 embedding_vector

后端：fuyao HTTP 图谱网关（无鉴权，支持 parameters）。契约见 references/gateway-api.md。

用法：
  python query.py -h
  python query.py search --query "稳定性压力测试" --label TestFactor --top-k 10
  python query.py cypher "MATCH (n:TS) RETURN n.ts_no AS no LIMIT 5"
  python query.py run similar_test_factor --param query="侧信道" --param top_k=5
  python query.py templates
  python query.py schema
"""

import argparse
import contextlib
import glob as _glob
import io
import json
import os
import re
import sys
import warnings

import requests
import yaml

from embed_config import EMBED_CONFIG, EMBED_LABELS, index_name

warnings.filterwarnings("ignore")  # 屏蔽自签 HTTPS / embedding SSL 警告

# ── 配置（可用环境变量覆盖）────────────────────────────────
GATEWAY_URL = os.getenv("GRAPH_GATEWAY_URL",
                        "https://fuyao.rnd.huawei.com/kg/v2/corecode/graph/query")
GRAPH_ID    = os.getenv("GRAPH_ID", "testdesign")
USER_ID     = os.getenv("GRAPH_USER_ID", "com.huawei.rnd.fuyao")
EMBED_URL   = os.getenv("EMBED_URL",
                        "http://service.coreai.rnd.huawei.com/prod/v-y3epb9a9fqco9db6/stream")
SEARCH_OVERSAMPLE = int(os.getenv("SEARCH_OVERSAMPLE", "10"))   # 向量检索超量倍数（超量取再按产品后过滤）


# ════════════════════════════════════════════════════════════
# 连接层：图谱网关 + embedding
# ════════════════════════════════════════════════════════════

def _strip_embedding(obj):
    """递归剔除所有 embedding_vector 键（大且无意义，不进返回值）"""
    if isinstance(obj, dict):
        return {k: _strip_embedding(v) for k, v in obj.items() if k != "embedding_vector"}
    if isinstance(obj, list):
        return [_strip_embedding(x) for x in obj]
    return obj


def post(statement, params=None, include_graph=False):
    """打图谱网关，返回原始 JSON payload"""
    contents = ["row", "graph"] if include_graph else ["row"]
    stmt = {"statement": statement, "resultDataContents": contents}
    if params:
        stmt["parameters"] = params
    body = {
        "graphify": True,
        "graph_id": GRAPH_ID,
        "user_id": USER_ID,
        "query": {"statements": [stmt]},
    }
    resp = requests.post(GATEWAY_URL, json=body, verify=False, timeout=60)
    resp.raise_for_status()
    return resp.json()


def parse_rows(payload):
    """网关 payload -> list[dict]（按列名 zip；剔 embedding_vector）"""
    data = payload.get("data", payload) if isinstance(payload, dict) else {}
    errors = data.get("errors") or []
    if errors:
        raise RuntimeError(f"gateway errors: {errors}")
    results = data.get("results") or []
    if not results:
        return []
    res0 = results[0]
    cols = res0.get("columns", [])
    rows = []
    for item in res0.get("data", []):
        rows.append(_strip_embedding(dict(zip(cols, item.get("row", [])))))
    return rows


def run_cypher(statement, params=None, include_graph=False):
    return parse_rows(post(statement, params, include_graph))


def embed_single(text):
    """单条文本 -> 向量（m3e 接口）"""
    data_init = {"prompt": "null", "batch_input": json.dumps([text])}
    resp = requests.post(EMBED_URL, json={"data": json.dumps(data_init)},
                         verify=False, timeout=30)
    resp.raise_for_status()
    result = json.loads(json.loads(resp.text[5:])["content"])
    if isinstance(result, dict):
        return result[text]
    return result[0]


# ════════════════════════════════════════════════════════════
# 模板注册表
# ════════════════════════════════════════════════════════════

def _templates_dir():
    env = os.getenv("TEST_GRAPH_TEMPLATES_DIR")
    if env:
        return env
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")


def load_templates():
    d = {}
    for path in sorted(_glob.glob(os.path.join(_templates_dir(), "*.yaml"))):
        with open(path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        if cfg and cfg.get("name"):
            d[cfg["name"]] = cfg
    return d


def _coerce(val, typ):
    if val is None:
        return None
    if typ == "int":
        return int(val)
    if typ == "float":
        return float(val)
    return str(val)


def run_template(name, params):
    tpls = load_templates()
    tpl = tpls.get(name)
    if not tpl:
        raise ValueError(f"模板 '{name}' 不存在；可用: {', '.join(tpls) or '(无)'}")
    cparams = {}
    for p in tpl.get("params", []):
        pname = p["name"]
        val = params.get(pname, p.get("default"))
        if p.get("required") and (val is None or val == ""):
            raise ValueError(f"模板 '{name}' 缺少必填参数: {pname}")
        if p.get("embed"):
            if val is None or val == "":
                raise ValueError(f"embed 参数 {pname} 不能为空")
            cparams["query_vector"] = embed_single(str(val))
        else:
            cparams[pname] = _coerce(val, p.get("type"))
    return run_cypher(_inject_product(tpl["cypher"]), cparams)


# ════════════════════════════════════════════════════════════
# 产品过滤：按节点到 Version(pbi_version_name) 的真实通路生成谓词
# ════════════════════════════════════════════════════════════
#
# 不改 sync、纯查询期过滤。各节点通路（逐边核对自 sync 脚本）：
#   A 类 TR/TS/TP/TC/DesignPrinciple：节点自带 pbi -> Version{pbi_version_id}
#   IR_SR：BELONGS_TO_VERSION 边（边上带 pbi）
#   资产 Scene/Function/TestFeature/TestFactor/Mode/SceneFactor：带 pbi 的「使用」边 -> Version
#   DesignFeature：唯一边 HAS_DESIGN_FEATURE 不带 pbi，只能 <-IR_SR-> BELONGS_TO_VERSION 兜到版本
# 通用谓词 = (node.pbi 支) OR (任意带 pbi 的相邻边支)，覆盖除 DesignFeature 外全部；后者特判。

def product_predicate(var: str = "n", label: str = None) -> str:
    """生成一个 EXISTS 布尔谓词：var 节点是否关联到 pbi_version_name 含 $product 的版本。"""
    if label == "DesignFeature":
        return (f"EXISTS {{ MATCH ({var})<-[:HAS_DESIGN_FEATURE]-(:IR_SR)-[r:BELONGS_TO_VERSION]->() "
                f"WHERE toLower(r.pbi_version_name) CONTAINS toLower($product) }}")
    return (
        f"(EXISTS {{ MATCH (v:Version {{pbi_version_id: {var}.pbi}}) "
        f"WHERE toLower(v.pbi_version_name) CONTAINS toLower($product) }} "
        f"OR EXISTS {{ MATCH ({var})-[e]-(), (v:Version {{pbi_version_id: e.pbi}}) "
        f"WHERE toLower(v.pbi_version_name) CONTAINS toLower($product) }})"
    )


_PF_TOKEN = re.compile(r"\{\{PRODUCT_FILTER:([A-Za-z_][A-Za-z0-9_]*)(?::([A-Za-z_]+))?\}\}")


def _inject_product(cypher: str) -> str:
    """把模板里的 {{PRODUCT_FILTER:var}} / {{PRODUCT_FILTER:var:Label}} 占位符替换为谓词。"""
    return _PF_TOKEN.sub(lambda m: product_predicate(m.group(1), m.group(2)), cypher)


# ════════════════════════════════════════════════════════════
# 图谱 schema（给 LLM 的自描述卡片）
# ════════════════════════════════════════════════════════════

_NODE_FIELDS = {
    "IR_SR":           ("requirement_alm_id", ["requirement_name", "requirement_type", "requirement_status", "requirement_parent_id"]),
    "Scene":           ("alm_id",             ["name", "description", "status", "alm_code"]),
    "Function":        ("alm_id",             ["function_name", "function_description", "function_status"]),
    "DesignFeature":   ("feature_id",         ["feature_name", "description", "feature_category", "status"]),
    "TestFeature":     ("feature_id",         ["feature_name"]),
    "SceneFactor":     ("factor_code",        ["factor_name", "factor_desc", "factor_data_type"]),
    "TestFactor":      ("test_factor_id",     ["name", "description", "logic_description", "precondition", "expected_result"]),
    "Mode":            ("mode_id",            ["name", "description", "mode_operation", "detection", "respond", "restore"]),
    "DesignPrinciple": ("id",                 ["mode_name", "mode_description", "asset_version"]),
    "Version":         ("pbi_version_id",     ["pbi_version_name", "product_id"]),
    "TR":              ("id",                 ["tr_name", "description", "resolve_description", "status"]),
    "TS":              ("id",                 ["ts_name", "resolve_description", "ts_type", "status"]),
    "TP":              ("id",                 ["tp_name", "description", "resolve_description", "status"]),
    "TC":              ("id",                 ["name", "description", "preparation", "test_step", "expect_output"]),
}

_RELATIONSHIPS = [
    ("IR_SR", "HAS_PARENT_IR", "IR_SR"),
    ("IR_SR", "BELONGS_TO_VERSION", "Version"),
    ("IR_SR", "HAS_FUNCTION", "Function"),
    ("IR_SR", "HAS_DESIGN_FEATURE", "DesignFeature"),
    ("IR_SR", "BELONGS_TO_SCENE", "Scene"),
    ("IR_SR", "HAS_TR", "TR"),
    ("IR_SR", "RELATES_TO_TP", "TP"),
    ("TR", "HAS_TEST_FEATURE", "TestFeature"),
    ("TR", "HAS_SCENE", "Scene"),
    ("TR", "HAS_TR_FUNCTION", "Function"),
    ("TR", "HAS_TS", "TS"),
    ("TS", "HAS_SCENE", "Scene"),
    ("TS", "HAS_TP", "TP"),
    ("TS", "HAS_TEST_FACTOR", "TestFactor"),
    ("TS", "HAS_SCENE_FACTOR", "SceneFactor"),
    ("TS", "HAS_MODE", "Mode"),
    ("TP", "HAS_TC", "TC"),
    ("TP", "HAS_TEST_FACTOR", "TestFactor"),
    ("TP", "HAS_SCENE_FACTOR", "SceneFactor"),
]


def get_schema():
    embed_map = {c["label"]: c["fields"] for c in EMBED_CONFIG}
    nodes = []
    for label, (key, fields) in _NODE_FIELDS.items():
        nodes.append({
            "label": label,
            "key": key,
            "fields": fields,
            "embedded": label in embed_map,
            "embed_fields": embed_map.get(label),
        })
    return {
        "database": GRAPH_ID,
        "nodes": nodes,
        "relationships": [{"from": a, "type": t, "to": b} for a, t, b in _RELATIONSHIPS],
        "vector_index_rule": "{label小写}_embedding_index（如 TestFactor -> testfactor_embedding_index）",
        "main_path": "IR_SR -> TR -> TS -> TP -> TC",
        "hint": "语义检索用 search 命令或 db.index.vector.queryNodes；只有 embedded=true 的节点可向量检索。",
    }


# ════════════════════════════════════════════════════════════
# 命令实现
# ════════════════════════════════════════════════════════════

def _parse_kv(items):
    d = {}
    for it in items or []:
        if "=" not in it:
            raise ValueError(f"--param 需要 k=v 格式: {it!r}")
        k, v = it.split("=", 1)
        d[k] = v
    return d


def cmd_cypher(args):
    params = _parse_kv(args.param)
    if args.product:
        params["product"] = args.product   # 供语句里引用 $product（原始语句需自行写过滤）
    payload = post(args.statement, params or None, include_graph=args.graph)
    if args.raw:
        return _strip_embedding(payload)
    return parse_rows(payload)


def cmd_search(args):
    if args.label not in EMBED_LABELS:
        raise ValueError(f"label {args.label!r} 不可向量检索；可用: {', '.join(EMBED_LABELS)}")
    vec = embed_single(args.query)
    # 向量索引不支持预过滤：超量取候选，套产品谓词后过滤，再 LIMIT top_k
    fetch = max(args.top_k * args.oversample, args.top_k)
    pred = product_predicate("n", args.label)
    rows = run_cypher(
        f"CALL db.index.vector.queryNodes($index, $fetch, $vec) YIELD node AS n, score "
        f"WHERE {pred} "
        f"RETURN n AS n, score ORDER BY score DESC LIMIT $k",
        {"index": index_name(args.label), "fetch": fetch, "vec": vec,
         "k": args.top_k, "product": args.product},
    )
    out = []
    for row in rows:
        node = row.get("n")
        if isinstance(node, dict):
            item = dict(node)
            item["score"] = row.get("score")
        else:
            item = {"n": node, "score": row.get("score")}
        out.append(item)
    return out


def cmd_run(args):
    return run_template(args.template, _parse_kv(args.param))


def cmd_templates(args):
    return [
        {"name": t["name"], "description": t.get("description", ""), "params": t.get("params", [])}
        for t in load_templates().values()
    ]


def cmd_schema(args):
    return get_schema()


# ════════════════════════════════════════════════════════════
# 入口：main(argv) -> str
# ════════════════════════════════════════════════════════════

def build_parser():
    p = argparse.ArgumentParser(
        prog="graph",
        description="testdesign 图谱查询：语义检索 / 原始 Cypher / 预置模板 / schema 自描述。",
    )
    sub = p.add_subparsers(dest="cmd")

    c = sub.add_parser("cypher", help="执行原始 Cypher（最灵活）")
    c.add_argument("statement", help="Cypher 语句")
    c.add_argument("--param", action="append", default=[], metavar="K=V",
                   help="参数，可多次；如 --param top_k=10")
    c.add_argument("--graph", action="store_true", help="同时返回子图 nodes/relationships")
    c.add_argument("--raw", action="store_true", help="返回网关原始结构（向量已剔除），用于校准")
    c.add_argument("--product", help="产品名，绑定为 $product 供语句引用（原始语句需自行写过滤）")
    c.set_defaults(func=cmd_cypher)

    s = sub.add_parser("search", help="语义向量检索（任意已向量化节点，限定产品）")
    s.add_argument("--query", required=True, help="查询文本（自然语言）")
    s.add_argument("--label", required=True, help="节点标签，见 schema；如 TestFactor / TS / TP")
    s.add_argument("--product", required=True, help="产品名，按关联版本 pbi_version_name 过滤（必填）")
    s.add_argument("--top-k", type=int, default=10, dest="top_k", help="返回条数（默认 10）")
    s.add_argument("--oversample", type=int, default=SEARCH_OVERSAMPLE,
                   help=f"超量倍数，产品占比小时调大（默认 {SEARCH_OVERSAMPLE}）")
    s.set_defaults(func=cmd_search)

    r = sub.add_parser("run", help="执行预置模板（见 templates）")
    r.add_argument("template", help="模板名")
    r.add_argument("--param", action="append", default=[], metavar="K=V",
                   help="模板参数，可多次；如 --param query=侧信道 --param top_k=5")
    r.set_defaults(func=cmd_run)

    t = sub.add_parser("templates", help="列出所有预置模板（名+描述+参数）")
    t.set_defaults(func=cmd_templates)

    h = sub.add_parser("schema", help="输出图谱结构（节点/字段/关系）")
    h.set_defaults(func=cmd_schema)

    return p


def _envelope(ok, action, data, error=None):
    count = len(data) if isinstance(data, list) else None
    return json.dumps(
        {"ok": ok, "action": action, "count": count, "data": data, "error": error},
        ensure_ascii=False, indent=2,
    )


def main(argv):
    """统一入口：一串命令行参数进，一个字符串出。exe 与 skill 都调它。"""
    parser = build_parser()
    if not argv:
        return parser.format_help()

    # 捕获 argparse 的 -h / 参数错误：它们会 print + sys.exit，这里收成文本返回
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            args = parser.parse_args(argv)
    except SystemExit as e:
        text = buf.getvalue()
        return text if text else f"exit {e.code}"

    if not getattr(args, "func", None):
        return parser.format_help()

    try:
        data = args.func(args)
    except Exception as e:  # 运行期错误 -> 信封 ok:false，绝不抛裸异常
        return _envelope(False, args.cmd, None, error=f"{type(e).__name__}: {e}")
    return _envelope(True, args.cmd, data)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # 保证跨平台输出干净 UTF-8（Windows 默认 cp936）
    except Exception:
        pass
    print(main(sys.argv[1:]))
