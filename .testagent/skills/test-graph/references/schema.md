# testdesign 图谱 Schema 卡片

图谱库 `testdesign`。检索前先看这张卡片，确认要查的节点/字段/关系。
运行 `python scripts/query.py schema` 可拿到结构化 JSON 版本。

## 节点（14 类，13 类已向量化）

`embed_fields` 为进入向量的字段（只放语义主字段）；其余字段仍存于图，检索可正常返回，只是不参与语义匹配。
只有 `embedded=true` 的节点能用 `search` 做语义检索。

| 节点 | key | 主要字段 | 向量化字段 |
|---|---|---|---|
| IR_SR 需求 | requirement_alm_id | requirement_name, type, status, parent_id | requirement_name |
| Scene 场景 | alm_id | name, description, status, alm_code | name, description |
| Function 功能 | alm_id | function_name, function_description, status | function_name, function_description |
| DesignFeature 设计特性 | feature_id | feature_name, description, category, status | feature_name, description |
| TestFeature 测试特性 | feature_id | feature_name | feature_name |
| SceneFactor 场景因子 | factor_code | factor_name, factor_desc, data_type | factor_name, factor_desc |
| TestFactor 测试因子 | test_factor_id | name, description, logic_description, precondition, expected_result | name, description |
| Mode 攻击模式 | mode_id | name, description, mode_operation, detection, respond, restore | name, description |
| DesignPrinciple 设计原则 | id | mode_name, mode_description, asset_version | mode_name, mode_description |
| Version 版本 | pbi_version_id | pbi_version_name, product_id | —（未向量化） |
| TR 测试需求 | id | tr_name, description, resolve_description, status | tr_name, description, resolve_description |
| TS 测试规格 | id | ts_name, resolve_description, ts_type, status | ts_name, resolve_description |
| TP 测试点 | id | tp_name, description, resolve_description, status | tp_name, description, resolve_description |
| TC 测试用例 | id（内部主键）；case_id（业务编号） | case_id, name, description, preparation, test_step, expect_output, status | name, description |

## 关系（19 条）

```
(IR_SR)-[:HAS_PARENT_IR]->(IR_SR)
(IR_SR)-[:BELONGS_TO_VERSION]->(Version)
(IR_SR)-[:HAS_FUNCTION]->(Function)
(IR_SR)-[:HAS_DESIGN_FEATURE]->(DesignFeature)
(IR_SR)-[:BELONGS_TO_SCENE]->(Scene)
(IR_SR)-[:HAS_TR]->(TR)
(IR_SR)-[:RELATES_TO_TP]->(TP)
(TR)-[:HAS_TEST_FEATURE]->(TestFeature)
(TR)-[:HAS_SCENE]->(Scene)
(TR)-[:HAS_TR_FUNCTION]->(Function)
(TR)-[:HAS_TS]->(TS)
(TS)-[:HAS_SCENE]->(Scene)
(TS)-[:HAS_TP]->(TP)
(TS)-[:HAS_TEST_FACTOR]->(TestFactor)
(TS)-[:HAS_SCENE_FACTOR]->(SceneFactor)
(TS)-[:HAS_MODE]->(Mode)
(TP)-[:HAS_TC]->(TC)
(TP)-[:HAS_TEST_FACTOR]->(TestFactor)
(TP)-[:HAS_SCENE_FACTOR]->(SceneFactor)
```

主链路：`IR_SR → TR → TS → TP → TC`，旁挂 Scene / Function / Feature / Factor / Mode。

## 向量索引

- 索引名规则：`{label小写}_embedding_index`（如 `TestFactor` → `testfactor_embedding_index`）。
- 检索：`CALL db.index.vector.queryNodes($index, $top_k, $query_vector) YIELD node, score`。
- `search` 命令已封装「文本 → 向量 → 查索引」，一般不用手写。

## 产品/版本关联（产品过滤依据）

产品过滤 = 节点关联的 `Version.pbi_version_name` 含产品名。各节点到 Version 的通路不同（`pbi` 值 = `Version.pbi_version_id`）：

| 类别 | 节点 | 到版本的通路 |
|---|---|---|
| A 工作项 | TR, TS, TP, TC, DesignPrinciple | 节点自带 `pbi` → `Version{pbi_version_id: n.pbi}` |
| B 需求 | IR_SR | `BELONGS_TO_VERSION` 边（边上有 `pbi` / `pbi_version_name`），可属多版本 |
| C 资产 | Scene, Function, TestFeature, TestFactor, Mode, SceneFactor | 带 `pbi` 的「使用」边（HAS_TEST_FACTOR / HAS_MODE / HAS_SCENE / HAS_TR_FUNCTION / HAS_TEST_FEATURE / HAS_SCENE_FACTOR）→ Version |
| C 特殊 | DesignFeature | 其边 `HAS_DESIGN_FEATURE` **不带 pbi**，须 `←IR_SR→BELONGS_TO_VERSION` 兜到版本 |

`search` / 模板已内置对应过滤谓词（模板里用 `{{PRODUCT_FILTER:var}}` 占位符，DesignFeature 用 `{{PRODUCT_FILTER:var:DesignFeature}}`）。写原始 `cypher` 时需自行按上表加过滤。
