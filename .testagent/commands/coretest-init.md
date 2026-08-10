---
description: 初始化 coretest-spec-e2e 测试设计任务上下文。
---

# coretest-init

解析用户输入的产品版本，并通过 `task` 工具调用 `coretest-init-agent`。

## 使用方式

```text
/coretest-init "UPCF 27.0.0"
```

## 执行步骤

1. 从用户输入中解析必填的产品版本名称。
2. 使用 `task` 工具调用 `coretest-init-agent`。
3. 传入 `product_name = 用户输入的产品版本`。
4. 等待 Agent 返回初始化结果。

