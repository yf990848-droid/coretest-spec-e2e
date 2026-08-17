# fuyao 图谱 HTTP 网关契约

test_graph-cli 查询 testdesign 图谱走 fuyao HTTP 网关（非 bolt 直连）。本文归档其请求/响应契约，供连接层实现与排障参考。

## Endpoint

```
POST https://fuyao.rnd.huawei.com/kg/v2/corecode/graph/query
Content-Type: application/json
```

- **无鉴权**：内网直通，`user_id` 放在 body 里即可，不需要 token / Authorization 头。
- 走 HTTPS 自签，客户端 `verify=False`。

## 请求体

```json
{
    "graphify": true,
    "graph_id": "testdesign",
    "user_id": "com.huawei.rnd.fuyao",
    "query": {
        "statements": [
            {
                "statement": "<Cypher>",
                "parameters": { "top_k": 10, "query_vector": [/* 768 floats */] },
                "resultDataContents": ["row"]
            }
        ]
    }
}
```

- **支持 `parameters`**：`$` 占位符绑定，向量检索的 768 维向量直接当参数传，无需拼进语句字符串。
- `resultDataContents`：`["row"]` 只要行数据；需要子图（节点+关系）时加 `"graph"`，返回体会多一份 `graph`。
- `graphify: true` 时才有 `graph` 段。

## 响应体

外层是 fuyao 包装（`code/msg/data`），`data` 内是 **Neo4j 标准事务 API** 结构：

```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "results": [
            {
                "columns": ["n"],
                "data": [
                    {
                        "row": [ { /* 若 RETURN 整节点，则是全属性 map */ } ],
                        "meta": [ { "id": 0, "type": "node", "deleted": false } ],
                        "graph": { "nodes": [...], "relationships": [] }
                    }
                ]
            }
        ],
        "errors": [],
        "lastBookmarks": ["FB:..."]
    }
}
```

解析路径：`data.results[0].columns` 为列名，`data.results[0].data[].row` 为各行值，按列名 zip 成 `dict`。
错误在 `data.errors`（非空即失败，需抛出）。

## ⚠️ embedding_vector 必须剔除

`RETURN n`（整节点）会把节点全部属性带出来，**包含 `embedding_vector`（768 个浮点数）**。它体积大、对下游（尤其 LLM 上下文）毫无意义，务必去掉。

两条防线：

1. **连接层统一兜底**：解析响应时递归删除所有 `embedding_vector` 键（`row` 值、`graph.nodes[].properties` 都要清）。
2. **模板/查询侧**：优先 `RETURN` 明确字段（如 `n.ts_no, n.ts_name, score`），不要 `RETURN n`；确需整节点时，靠第 1 条兜底。

> 归档样例中的 `embedding_vector` 已被手动置空 `[]`，真实响应里是一长串数字。文档与日志里都不要保留原始向量。

## 备注

- 响应结构若与本文不一致（网关版本变动），用 CLI 的 `--raw` 直接打印未处理 JSON 校准后再更新本文。
- 真实样例见本次 TS 查询：`MATCH (n:TS) RETURN n LIMIT 1`（label=TS, ts_no=TS20250920000038）。
