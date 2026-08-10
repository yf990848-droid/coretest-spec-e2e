---
description: 初始化 coretest-spec-e2e
  测试设计任务上下文。解析产品版本并通过 task 工具调用
  coretest-init-agent 执行初始化流程。
metadata:
  author: corespec
  version: 1.2.0
name: coretest-init
---

# coretest-init

## 用途

作为 Web 端初始化入口，解析用户输入的产品版本，并通过 `task` 工具调用
`coretest-init-agent` 完成测试设计上下文初始化流程。

此 Skill 只负责用户入口和 Agent 调度。

## 使用方式

``` text
/coretest-init "UPCF 27.0.0"
```

## 输入

-   `产品版本`：必填，例如 `UPCF 27.0.0`

## 执行步骤

1.  从用户输入中解析产品版本名称。

2.  使用 `task` 工具调用：

``` text
coretest-init-agent
```

3.  向 Agent 传入：

``` text
product_name = 用户输入的产品版本
```

4.  等待 Agent 完成初始化流程。

## 调用要求

必须使用 `task` 工具调用 `coretest-init-agent`
执行初始化流程。

## 输出

由 `coretest-init-agent` 返回初始化结果。
