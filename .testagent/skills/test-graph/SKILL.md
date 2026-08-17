---
name: test-graph
description: >-
  查询 testdesign 测试设计知识图谱（需求 IR_SR、测试需求 TR、测试规格 TS、测试点 TP、测试用例 TC，
  以及场景/功能/特性/因子/攻击模式）。在分析需求文档、explore 疑问、需要补充上下文时使用：检索历史相似
  测试因子（TestFactor）、查需求/SR 官方定义、按语义找相似的 TS/TP/TC、或对图谱执行自定义 Cypher。
  当遇到不理解的特性/功能/场景、需要复用历史测试资产、或要顺着需求追溯到测试规格/用例时，用它。
---

# test-graph

查询 testdesign 图谱的四类能力，统一入口 `scripts/query.py`，返回 JSON 信封字符串。

> **检索一律限定产品**：`search` 和 `run` 都必须带产品名，按节点关联版本的 `pbi_version_name` 过滤。

## 快速上手

```bash
# 语义检索：在某产品下找相似的历史测试因子（最常用）
python scripts/query.py search --query "稳定性压力测试" --label TestFactor --product UEG --top-k 10

# 自定义 Cypher（最灵活；原始语句需自行写过滤，--product 会绑定为 $product）
python scripts/query.py cypher "MATCH (n:TS) RETURN n.ts_no AS no, n.ts_name AS name LIMIT 5"
```

返回统一是 JSON 信封：
```json
{"ok": true, "action": "search", "count": 2,
 "data": [{"id": "...", "name": "...", "score": 0.83}], "error": null}
```
出错时 `{"ok": false, "data": null, "error": "..."}`。

## 命令一览（逐层 -h 查细节）

| 命令 | 用途 |
|---|---|
| `search --query <文本> --label <节点> --product <产品> [--top-k N] [--oversample N]` | 语义向量检索（限定产品），任意已向量化节点 |
| `cypher "<语句>" [--param k=v] [--product P] [--graph] [--raw]` | 原始 Cypher 透传 |
| `run <模板> [--param k=v]` | 执行预置场景模板 |
| `templates` | 列出所有预置模板 |
| `schema` | 输出图谱结构（节点/字段/关系） |

任意层级加 `-h` 查看用法：`python scripts/query.py -h`、`python scripts/query.py search -h`。

## 按需深入（progressive disclosure）

- **不确定图里有什么节点/字段/关系** → 先跑 `schema`，或读 `references/schema.md`。
- **想用现成的场景查询** → 跑 `templates` 看清单；写新模板见 `references/templates.md`。
- **要写复杂 Cypher / 排查网关返回** → 读 `references/gateway-api.md`（含返回结构、`--raw` 校准、embedding_vector 已剔除说明）。

## 要点

- **产品名必填**：按节点关联版本的 `pbi_version_name` 过滤（大小写不敏感、包含匹配）。所有节点都能关联到产品（A 类工作项经自身 pbi、IR_SR/资产经带 pbi 的边、DesignFeature 经 IR_SR）。
- 只有 `schema` 中 `embedded=true` 的节点可用 `search`（如 TestFactor / TS / TP / TC / Scene…）。
- 语义检索首选场景：**历史相似测试因子** → `search --label TestFactor --product <产品>` 或 `run similar_test_factor`。
- 产品占比小、`search` 结果不足 `top_k` 时，调大 `--oversample`。
- 需求追溯链路：`IR_SR → TR → TS → TP → TC`，可用 `cypher` 顺着关系查（自行加产品过滤）。
- 首次使用需装依赖：`pip install -r requirements.txt`（requests, pyyaml）。
