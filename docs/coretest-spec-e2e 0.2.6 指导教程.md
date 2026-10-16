# coretest-spec-e2e 0.2.6 指导教程

> 适用版本：`coretest-spec-e2e 0.2.6`  
> 推荐流程：Init → Explore → Design → Archive

## 1. 0.2.6 更新说明

0.2.6 在 0.2.5 因子关联闭环基础上适配公司新版测试用例卡片，采用最小改动方案：

- 仅替换新版测试用例卡片对应的 `webapps`；
- 不修改 Init、Explore、Design、Archive 主流程；
- 不改变 TS/TP/TC Markdown、JSON 产物结构和标准目录；
- 保留 0.2.5 已实现的 TestFactor/SceneFactor 检索、因子计划和 Archive 关联能力；
- 保留全量测试设计卡片触发能力：
  - TR 节点【AI分析】→ `/coretest-explore`
  - TS 节点【AI分析】→ `/coretest-design`
  - TR → 关联对象 → 关联的 TS，可多选 TS 后点击【AI分析】批量触发 Design；
- 新版测试用例卡片加载、现有测试用例展示和 Design 卡片链路已验证通过。

## 2. 使用前准备

使用扩展包前请确认：

1. TestAgent 已加载 `coretest-spec-e2e 0.2.6`；
2. 当前账号有对应产品版本、测试设计任务和 Portal 权限；
3. CoreTool CLI 已完成登录；
4. 当前 TR 已在全量测试设计平台创建，并正确关联 IR/SR/US，以及需要的特性或功能。

CoreTool CLI 登录：

```powershell
.testagent\skills\coretool-cli\tools\coretool-cli.exe auth login
```

登录后可检查状态：

```powershell
.testagent\skills\coretool-cli\tools\coretool-cli.exe auth status
```

详细说明见：[`CORETOOL_CLI_LOGIN.md`](./CORETOOL_CLI_LOGIN.md)。

## 3. 总体流程

```text
/coretest-init
    ↓
选择/创建 TR
    ↓
/coretest-explore
    ↓
生成普通 TS + 获取平台 DFX TS
    ↓
可选：归档 Explore 生成的普通 TS
    ↓
/coretest-design
    ↓
生成 TP/TC + 因子候选 + 因子计划
    ↓
/coretest-archive
    ↓
对象归档 + 因子关联 + 在线文档同步 + Portal 刷新
```

---

## 4. coretest-init：初始化设计任务

### 4.1 命令

```text
/coretest-init "UPCF 27.0.0"
```

### 4.2 执行内容

Agent 会自动：

- 查询产品版本对应 PBI；
- 拉取当前用户可用的测试设计任务；
- 获取已有 TR；
- 获取 TR 直接关联的需求信息；
- 展示全量测试设计平台卡片。

如果还没有目标 TR，请先在右侧全量测试设计卡片中按产品现有流程创建 TR，并完成需求、特性或功能关联。

TR 创建完成后，可在左侧对话区输入：

```text
TR已创建
```

Agent 会重新拉取最新 TR 信息。

如果 TR 已经存在，也可以直接进入 Explore：

```text
/coretest-explore 4029
```

---

## 5. coretest-explore：生成测试规格和 TS

Explore 有两种入口。

### 5.1 方式一：卡片触发

在全量测试设计卡片的 TR 节点右键点击【AI分析】。

系统会自动生成并发送：

```text
/coretest-explore <TR ID>
```

### 5.2 方式二：手工命令

```text
/coretest-explore <tr_id>
```

例如：

```text
/coretest-explore 4029
```

### 5.3 Explore 会做什么

Agent 会：

1. 读取 TR 直接关联需求；
2. 下载并解析需求/设计文档；
3. 生成普通测试规格；
4. 查询平台已有 DFX TS；
5. 将普通 TS 与 DFX TS 统一编号并写入 `ts_catalog.json`；
6. 展示本轮 TS；
7. 询问是否将 Explore 生成的普通 TS 归档到全量测试设计平台。

> DFX TS 是平台已有对象，不会在 Explore 阶段重复创建。

如果后续希望从 Portal 卡片直接触发 Design，建议在这里选择“直接归档全部普通 TS”，使普通 TS 获得真实平台 ID。

### 5.4 主要产物

```text
.design_output/<design_task_id>/TR_<tr_id>/
├── 系统需求.md
├── 功能设计.md
├── sr_specs/
└── test_specs/
    ├── platform_ts.json
    ├── tr_ts.json
    └── ts_catalog.json
```

---

## 6. coretest-design：生成 TP/TC 和因子计划

Design 有三种入口。

### 6.1 方式一：单 TS 卡片触发

在全量测试设计卡片的 TS 节点右键点击【AI分析】。

系统会自动触发指定 TS 的 Design 流程。

### 6.2 方式二：卡片批量选择 TS

在 TR 节点进入：

```text
关联对象 → 关联的 TS
```

多选目标 TS 后点击【AI分析】，可批量触发 Design。

### 6.3 方式三：手工命令

处理指定 TS：

```text
/coretest-design 4029 TS_18
```

处理多个 TS：

```text
/coretest-design 4029 TS_11 TS_12
```

也可使用真实平台 TS ID：

```text
/coretest-design TR_4029 TS_40152
```

### 6.4 Design 会做什么

每个 TS 独立完成：

1. 读取对应测试规格；
2. 生成测试设计 Markdown；
3. 生成 TP/TC；
4. 查询因子库；
5. 生成因子候选文件；
6. 根据设计内容选择关联因子并生成因子计划；
7. 校验因子计划；
8. 更新测试用例卡片。

每批最多并行处理 3 个 TS。

### 6.5 因子规则（0.2.5 起）

| TS 类型 | TS/TP 可使用的因子 |
|---|---|
| scene | TestFactor + SceneFactor |
| function / constraint / feature / DFX | TestFactor |
| 图谱无匹配 | 允许空因子继续 |

Design 阶段只生成本地计划，**不会直接修改平台因子关系**；真实平台关联在 Archive 阶段执行。

### 6.6 主要产物

```text
test_design/
├── ts_<NN>_test_design.md
├── ts_<NN>_test_cases.md
├── ts_<NN>_tp.json
├── ts_<NN>_tc.json
├── ts_<NN>_factor_candidates.json
└── ts_<NN>_factor_plan.json
```

其中：

- `factor_candidates.json`：记录实际因子查询及候选结果；
- `factor_plan.json`：记录最终 TS/TP 因子关联计划。

---

## 7. coretest-archive：归档对象、因子和文档

### 7.1 命令格式

```text
/coretest-archive <tr_id> <归档目标...>
```

常用示例：

```text
/coretest-archive 4029 TR
/coretest-archive 4029 TS
/coretest-archive 4029 TS_18
/coretest-archive 4029 TP
/coretest-archive 4029 TS_18/TP.18.01
/coretest-archive 4029 TC
```

### 7.2 目标范围

| 输入 | 实际处理范围 |
|---|---|
| `TR` | 复用 TR，并同步任务/TR 文档 |
| `TS` | 全部 TS |
| `TS_<NN>` | 指定 TS |
| `TP` | 全部 TS + TP |
| `TS_<NN>/TP.xxx` | 所属 TS + 指定 TP |
| `TC` | 全部 TS + TP + TC |

指定对象时只自动补齐父级依赖，不会向下扩展无关对象。

### 7.3 Archive 因子处理（0.2.5 起）

正式 Archive 中：

1. TS 创建成功或从状态复用；
2. 根据 `factor_plan.json` 查询 TS 已有关联因子；
3. 已存在的关系直接复用；
4. 缺失的关系写入平台；
5. 新 TP 创建时通过 `--relations` 一次性携带 TP 因子关系；
6. 对象和因子结果写入 `archive_state.json`。

注意：

- 已成功旧 TP 不补录因子；
- 重跑时已成功对象直接复用；
- TS 因子仍会执行平台查询，避免重复创建关系；
- TestFactor 使用真实因子 UUID，不使用 TS 关系数字 ID。

### 7.4 Archive 完整编排

```text
对象归档
    ↓
TS 因子同步 / 新 TP 原子关联
    ↓
在线文档同步
    ↓
Portal 卡片刷新
    ↓
最终汇总
```

归档完成后，右侧 Portal 卡片会跳转到本次最后成功的目标对象，可查看对象和已同步文档。

---

## 8. 归档状态和断点续跑

归档状态保存在：

```text
.design_output/<design_task_id>/TR_<tr_id>/archive/archive_state.json
```

如果流程中途失败，不需要清空状态文件。

修复问题后使用相同 TR 和目标重新执行即可，例如：

```text
/coretest-archive 4029 TS_18/TP.18.01
```

流程会：

- 复用已经成功的 TR/TS/TP；
- 继续处理失败或未执行对象；
- 查询并复用已有因子关系；
- 避免重复创建已成功对象。

---

## 9. 常见问题

### 9.1 CoreTool 提示未登录

执行：

```powershell
.testagent\skills\coretool-cli\tools\coretool-cli.exe auth login
```

然后重新运行原命令。

### 9.2 Design 没有选到因子，是否代表失败？

不是。

只要因子查询正常执行且没有匹配结果，0.2.5 起允许生成空因子计划，并继续 TP/TC 设计。

### 9.3 为什么已有 TP 没有补上新因子？

0.2.5 起的规则是：

- 新 TP：创建时原子关联因子；
- 已成功旧 TP：直接复用，不做补录。

### 9.4 为什么 Explore 不创建 DFX TS？

DFX TS 已存在于平台。Explore 只查询并纳入统一 catalog，正式 Archive 同样复用其真实平台 ID。

### 9.5 Archive 中断后是否需要删除 archive_state.json？

不需要。

`archive_state.json` 用于保证断点续跑和避免重复创建，应保留后直接重试。

---

## 10. 推荐操作顺序

首次完整使用建议按以下顺序：

```text
1. /coretest-init "产品版本"
2. 在平台确认或创建 TR
3. /coretest-explore <tr_id>
4. 归档 Explore 普通 TS（需要卡片触发 Design 时建议执行）
5. /coretest-design <tr_id> <TS...>
6. 检查 TP/TC 和因子计划
7. /coretest-archive <tr_id> <目标...>
8. 在 Portal 检查对象、因子和在线文档
```

0.2.6 已在 0.2.5 scene TS 完整闭环验证基础上完成新版测试用例卡片适配验证；Design → 因子计划 → TS 因子同步 → 新 TP 因子关联 → 在线文档 → Portal 的既有主链路保持不变。
