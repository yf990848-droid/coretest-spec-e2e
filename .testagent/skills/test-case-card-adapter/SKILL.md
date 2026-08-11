---
description: 将单个 TS 测试用例转换为测试用例卡片，并更新已初始化的 TS working 卡片。
metadata:
  author: corespec
  version: "2.5.0"
name: test-case-card-adapter
---

# 测试用例卡片适配 Skill

## 概述

用于连接：

```
coretest-design
        |
        v
.design_output/<design_task_id>/TR_<tr_id>/test_design/ts_<NN>_tc.json
        |
        v
.design_output/<design_task_id>/TR_<tr_id>/ts_<NN>_test_case.json
        |
        v
测试用例卡片
```

本 Skill 只处理单个 TS 的测试用例卡片转换与更新，不负责初始化 working 卡片，不负责遍历多个 TS，也不负责测试设计。

working 卡片必须在 `coretest-design` 启动 TS SubAgent 之前完成初始化。初始化时必须使用 TS 级 key：

```
<requirement_id>_<ts-id>
```

例如：

```
IR20251206000098_ts_01
```

初始化脚本会在以下目录生成对应 card_id 文件：

```
<root>/.testagent/skills/card-initializer/scripts/test_case/<requirement_id>_<ts-id>_card_id.txt
```

例如：

```
<root>/.testagent/skills/card-initializer/scripts/test_case/IR20251206000098_ts_01_card_id.txt
```

---

## 职责

本 Skill 负责：

1. 读取当前 TS 的测试用例 JSON：

   ```
   .design_output/<design_task_id>/TR_<tr_id>/test_design/ts_<NN>_tc.json
   ```

2. 检查当前 TS 已初始化的 card_id 文件：

   ```
   <root>/.testagent/skills/card-initializer/scripts/test_case/<requirement_id>_<ts-id>_card_id.txt
   ```

3. 调用 `prepare_test_case_card.py`，将当前 TS 测试用例 JSON 转换为测试用例卡片数据文件：

   ```
   .design_output/<design_task_id>/TR_<tr_id>/ts_<NN>_test_case.json
   ```

4. 调用 `test-case-card` 的 `card_generate.py`，通过第 4 个参数传入当前 TS 级 key，将当前 TS 的 working 卡片更新为 completed 状态。

---

## 输入参数

### --root

扩展包根目录。

示例：

```
D:\TestAgent\templates\coretest-spec-e2e@0.1.2\coretest-spec-e2e
```

### --ir-id

需求编号 `requirement_id`，兼容 IR/SR。参数名为保持现有脚本调用兼容而保留。

示例：

```
IR20251206000098（SR 场景可传 SR20260124957173）
```

### --ts-id

TS 编号。

示例：

```
ts_01
```

### --tc-json

当前 TS 测试用例 JSON 文件路径。

示例：

```
.design_output/2470/TR_3863/test_design/ts_01_tc.json
```

### --spec-file

测试规格文件路径。

### --cida-info

init 阶段生成并由 explore 阶段落入当前上下文目录的 CIDA 文件路径：

```
.design_output/<design_task_id>/TR_<tr_id>/cida_info.json
```

必须使用该文件，只读，不得重新生成或覆盖，也不得改用 `test-case-card/config/cida_info.json`。

### --output

当前 TS 测试用例卡片数据输出路径：

```
.design_output/<design_task_id>/TR_<tr_id>/ts_<NN>_test_case.json
```

---

## 派生路径

根据输入参数派生 TS 级卡片 key：

```
<requirement_id>_<ts-id>
```

例如：

```
IR20251206000098_ts_01
```

根据该 key 派生 card_id 文件路径：

```
<root>/.testagent/skills/card-initializer/scripts/test_case/<requirement_id>_<ts-id>_card_id.txt
```

例如：

```
D:\TestAgent\templates\coretest-spec-e2e@0.1.2\coretest-spec-e2e\.testagent\skills\card-initializer\scripts\test_case\IR20251206000098_ts_01_card_id.txt
```

---

## 执行流程

### 第一步：检查输入文件

检查以下文件必须存在：

```
<tc-json>
<spec-file>
<cida-info>
<root>/.testagent/skills/card-initializer/scripts/test_case/<requirement_id>_<ts-id>_card_id.txt
```

如果任一文件不存在，必须停止当前 TS 的卡片生成，并返回明确错误原因。

---

### 第二步：生成当前 TS 的测试用例卡片数据

调用：

```
.testagent/skills/test-case-card-adapter/scripts/prepare_test_case_card.py
```

要求：

- 只处理当前 TS；
- 只读取当前 `ts_<NN>_tc.json`；
- 只生成当前 `ts_<NN>_test_case.json`；
- 不合并多个 TS。

推荐执行方式：

```powershell
cd <root>; python .\.testagent\skills\test-case-card-adapter\scripts\prepare_test_case_card.py `
  --root "<root>" `
  --ir-id "<requirement_id>" `
  --ts-id "<ts-id>" `
  --tc-json "<tc-json>" `
  --spec-file "<spec-file>" `
  --output "<output>"
```

输出：

```
.design_output/<design_task_id>/TR_<tr_id>/ts_<NN>_test_case.json
```

---

### 第三步：调用 test-case-card 更新卡片

调用：

```
.testagent/skills/test-case-card/scripts/card_generate.py
```

必须按照 test-case-card 原有成功路径执行，进入脚本目录后再执行脚本，并通过第 4 个参数传入当前 TS 级 key。

执行方式要求：

```powershell
cd <root>\.testagent\skills\test-case-card\scripts; python -u card_generate.py `
  "<root>\.design_output\<design_task_id>\TR_<tr_id>\ts_<NN>_test_case.json" `
  "<spec-file>" `
  "<cida-info>" `
  "<requirement_id>_<ts-id>"
```

示例：

```powershell
cd D:\TestAgent\templates\coretest-spec-e2e@0.1.6\coretest-spec-e2e\.testagent\skills\test-case-card\scripts; python -u card_generate.py `
  "D:\TestAgent\templates\coretest-spec-e2e@0.1.6\coretest-spec-e2e\.design_output\2470\TR_3863\ts_01_test_case.json" `
  "D:\TestAgent\templates\coretest-spec-e2e@0.1.6\coretest-spec-e2e\.design_output\2470\TR_3863\test_specs\NsmfNupf链路容灾功能补齐测试规格.md" `
  "D:\TestAgent\templates\coretest-spec-e2e@0.1.6\coretest-spec-e2e\.design_output\2470\TR_3863\cida_info.json" `
  "IR20251206000098_ts_01"
```

要求：

- 不直接在任意目录用绝对路径调用 `card_generate.py`；
- 必须先 `cd` 到 `test-case-card/scripts` 目录；
- 命令间隔必须使用 `;`；
- 不得使用 `&&`；
- 当前 TS 的初始化 key 必须是 `<requirement_id>_<ts-id>`；
- 第 4 个参数必须传入 `<requirement_id>_<ts-id>`；
- 第 3 个参数必须使用 `<cida-info>`，不得使用 Skill 配置目录中的旧 CIDA；
- 只更新当前 TS 的卡片。

---

## 输出

成功后，当前 TS 的卡片状态应从 working 更新为 completed。

示例：

```
TS01 -> completed 测试用例卡片
```

失败时，返回当前 TS 的失败原因，不影响其他 TS 的设计和卡片生成。

---

## 约束

- 一个 Skill 调用只处理一个 TS；
- card_id 文件统一由 `card-initializer/scripts/test_case/card_generate.py` 生成并保留在初始化脚本目录；
- 调用 `test-case-card/scripts/card_generate.py` 时必须传入第 4 个参数 `<requirement_id>_<ts-id>`；
- 卡片初始化必须由 `coretest-design` 在 TS SubAgent 并行启动前完成。
