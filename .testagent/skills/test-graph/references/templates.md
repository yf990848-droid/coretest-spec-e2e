# 预置查询模板

模板把常用场景查询写成声明式数据（`templates/*.yaml`），用 `run <name>` 执行。
`python scripts/query.py templates` 可列出当前所有模板。

## 现有模板

> **所有模板都必须带 `product`**（按关联版本 `pbi_version_name` 过滤，见下方「产品过滤」）。

**语义 / 关键词检索**

| 模板 | 作用 | 参数 |
|---|---|---|
| `similar_test_factor` | 历史相似测试因子检索（语义） | `query`(必填), **`product`(必填)**, `top_k`(默认10) |
| `sr_definition` | 按关键词查需求/SR 官方定义 | `keyword`(必填), **`product`(必填)**, `limit`(默认10) |

**关系追溯**（顺链路/邻居查，手写 Cypher 麻烦，用模板）

| 模板 | 作用 | 参数 |
|---|---|---|
| `trace_ir_to_tests` | 需求全链路追溯 IR_SR→TR→TS→TP→TC | `requirement_alm_id`(必填), **`product`(必填)**, `limit`(默认200) |
| `ts_context` | 某 TS 关联的场景/因子/模式/测试点汇总 | `ts_id`(必填), **`product`(必填)** |
| `scene_test_specs` | 按场景名关键词找关联 TR/TS | `keyword`(必填), **`product`(必填)**, `limit`(默认20) |
| `factor_usage` | 某测试因子被哪些 TS/TP 使用 | `test_factor_id`(必填), **`product`(必填)** |

示例：
```
python scripts/query.py run similar_test_factor --param query="侧信道攻击" --param product=UEG --param top_k=5
python scripts/query.py run sr_definition   --param keyword=DLB --param product=UEG
python scripts/query.py run trace_ir_to_tests --param requirement_alm_id=SR-12345 --param product=UEG
python scripts/query.py run ts_context      --param ts_id=29377 --param product=UEG
python scripts/query.py run scene_test_specs --param keyword=Voice-Centric --param product=UEG
python scripts/query.py run factor_usage    --param test_factor_id=12345 --param product=UEG
```

> id 类参数需与图中存储类型一致（都是**字符串**，直接传）：
> TS/TR/TP/TC 的 `id`、IR_SR 的 `requirement_alm_id`、TestFactor 的 `test_factor_id` 均为字符串。
> （注意 TestFactor 节点上另有个数字 `id` 字段，别和匹配键 `test_factor_id` 混了。）

## 如何加一个模板

在 `templates/` 下新增一个 `.yaml`，代码零改动：

```yaml
name: <模板名>                # run <模板名> 调用
description: <一句话说明>
params:
  - {name: query, type: str, required: true, embed: true}   # embed=true -> 该参数先向量化，注入 $query_vector
  - {name: top_k, type: int, default: 10}
cypher: |
  CALL db.index.vector.queryNodes('testfactor_embedding_index', $top_k, $query_vector)
  YIELD node AS n, score
  RETURN n.test_factor_id AS id, n.name AS name, score
  ORDER BY score DESC
```

规则：
- **参数占位符**：cypher 里用 `$参数名`；类型 `int/float/str` 会自动转换。
- **`embed: true`**：该参数的文本会先过 embedding，结果以 `$query_vector` 注入（cypher 里写 `$query_vector`，不是 `$query`）。
- **RETURN 明确字段**，不要 `RETURN n`（避免带出 embedding_vector；连接层虽会兜底剔除，但明确字段更省更清晰）。
- 每个模板一个 `.yaml`，`name` 必须唯一。

## 产品过滤

所有检索限定在某产品内：按「节点关联的 Version 的 `pbi_version_name` 含产品名」过滤（大小写不敏感）。

- 声明一个 `product`（必填）参数。
- 在需要过滤的节点变量处放占位符 **`{{PRODUCT_FILTER:变量名}}`**，运行时自动替换为该节点到版本的过滤谓词。
  - 一般节点：`{{PRODUCT_FILTER:ts}}`（自动覆盖 node.pbi 与带 pbi 的相邻边两种通路）。
  - DesignFeature 特殊（其边不带 pbi，须经 IR_SR 兜版本）：写 `{{PRODUCT_FILTER:df:DesignFeature}}`。
- 谓词是 `EXISTS{...}` 存在性判断，可直接放进 `WHERE`（含 `OPTIONAL MATCH ... WHERE`）。

例：
```
MATCH (n:IR_SR) WHERE n.requirement_name CONTAINS $keyword AND {{PRODUCT_FILTER:n}}
```
