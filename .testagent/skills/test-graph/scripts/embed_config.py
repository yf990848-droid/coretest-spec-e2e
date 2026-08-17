"""
向量化节点配置（同步脚本与向量索引脚本共用，单一数据源）

新增/调整向量化节点时只改这里一处：
  label   图节点标签
  id      该节点的 MERGE key（属性名），用于写回向量
  fields  参与向量文本的属性，按顺序用「。」拼接（None/空串自动跳过）
          原则：只放语义主字段（name + 描述类），不要塞过程性长字段
          （test_step / preparation / mode_operation 等），避免拼接超
          m3e ~512 token 被截断、以及多字段稀释语义。过程字段仍随节点
          存在图里，检索时可正常返回，只是不进向量。

所有节点统一写入 embedding_vector 属性；
向量索引名规则见 index_name()，与索引初始化脚本一致。

注意：本模块需与两个脚本同目录、且脚本改名为 .py 后一起部署。
"""

EMBED_CONFIG = [
    {"label": "TS",              "id": "id",                 "fields": ["ts_name", "resolve_description"]},
    {"label": "TC",              "id": "id",                 "fields": ["name", "description"]},
    {"label": "TP",              "id": "id",                 "fields": ["tp_name", "description", "resolve_description"]},
    {"label": "TR",              "id": "id",                 "fields": ["tr_name", "description", "resolve_description"]},
    {"label": "Mode",            "id": "mode_id",            "fields": ["name", "description"]},
    {"label": "TestFactor",      "id": "test_factor_id",     "fields": ["name", "description"]},
    {"label": "Scene",           "id": "alm_id",             "fields": ["name", "description"]},
    {"label": "Function",        "id": "alm_id",             "fields": ["function_name", "function_description"]},
    {"label": "DesignFeature",   "id": "feature_id",         "fields": ["feature_name", "description"]},
    {"label": "SceneFactor",     "id": "factor_code",        "fields": ["factor_name", "factor_desc"]},
    {"label": "DesignPrinciple", "id": "id",                 "fields": ["mode_name", "mode_description"]},
    {"label": "IR_SR",           "id": "requirement_alm_id", "fields": ["requirement_name"]},
    {"label": "TestFeature",     "id": "feature_id",         "fields": ["feature_name"]},
]

# 只需要标签列表时用它（向量索引脚本用）
EMBED_LABELS = [c["label"] for c in EMBED_CONFIG]


def index_name(label: str) -> str:
    """向量索引命名规则：{label小写}_embedding_index（TS -> ts_embedding_index）"""
    return f"{label.lower()}_embedding_index"
