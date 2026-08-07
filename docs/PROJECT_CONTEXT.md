# CoreTest-spec-e2e 项目上下文

## 1. 项目目标

CoreTest-spec-e2e 是基于 TestAgent 的端到端智能测试设计能力扩展，目标是实现从需求输入到测试资产归档的自动化闭环：

```
需求 IR/SR
    ↓
coretest-init
    ↓
设计上下文初始化
    ↓
coretest-explore
    ↓
需求解析与测试规格生成
    ↓
coretest-design
    ↓
TS级测试设计与测试用例生成
    ↓
test-case-card
    ↓
测试设计过程卡片展示
    ↓
coretest-archive
    ↓
TR / TS / TP / TC 自动归档
```

项目目标：

- 减少人工测试设计工作量；
- 基于需求自动生成测试规格、测试点和测试用例；
- 实现测试资产自动归档；
- 建立需求到测试资产的端到端追踪链路。

## 2. 当前版本

当前版本：

```
coretest-spec-e2e 0.2.1
```

版本演进：

|版本|主要能力|
|-|-|
|0.1.x|打通需求探索、测试设计、卡片展示和归档基础流程|
|0.2.0|完善 E2E 测试设计流程，引入 TR/TS/TP/TC 自动化处理|
|0.2.1|优化 init 流程、支持 TR 驱动需求输入、增强 explore 与 TS 级设计闭环|

## 3. 核心能力

### coretest-init

能力：

- 根据产品版本获取设计任务信息；
- 获取 PBI、design_task、TR、IR/SR 关联关系；
- 初始化设计上下文；
- 支持已有 TR 查询，并支持创建后重新执行 init 获取最新关系。

核心产物：

```
.design_output/design_task_info.json
.design_output/<design_task_id>/<IR>/cida_info.json
```

### coretest-explore

生成：

```
系统需求.md
功能设计.md
测试规格.md
tr_ts.json
```

支持：

- IR/SR 输入；
- TR 关联需求解析；
- SR 文档下载；
- 多 SR 去重；
- 基于 TR 关系生成测试规格上下文。

### coretest-design

当前设计模式：TS 级并行闭环。

流程：

```
TS列表
 ↓
初始化TS working卡片
 ↓
调用test-design-agent
 ↓
生成TS测试设计
 ↓
提取TP/TC JSON
 ↓
更新测试用例卡片completed
```

每个 TS 输出：

```
ts_xx_test_design.md
ts_xx_test_cases.md
ts_xx_tp.json
ts_xx_tc.json
```

设计约束：

- 一个 TS 对应一个测试用例卡片；
- 同时最多处理 3 个 TS；
- TS Agent 只能生成自身负责 TS 的 TP/TC；
- TS 间通过完整 TS 列表保持职责边界。

### test-case-card-adapter

职责：

- 读取单个 TS 的 TC JSON；
- 生成测试用例卡片数据；
- 使用 TS 级 key 更新 working 卡片。

卡片关联规则：

```
<IR>_<ts-id>
```

例如：

```
IR20251206000098_ts_01
```

### coretest-archive

自动归档：

```
TR
 ↓
TS
 ↓
TP
 ↓
TC
```

特点：

- 自动补齐父级对象；
- archive_state.json 保存归档状态；
- 支持单对象精确归档。

## 4. 当前验证状态

已完成验证：

- init 流程验证完成；
- explore 流程验证完成；
- design TS 级生成流程验证完成；
- archive 基础流程验证完成。

验证示例：

```
IR:
IR20251206000098

TR:
3861

TS:
TS_01 / TS_02 / TS_14

TP:
18295
```

## 5. 当前问题与优化方向

### Portal 卡片显示问题

现象：

- 卡片缓存接口调用成功；
- 返回 card_cache_id；
- Portal 页面未正常展示。

需要排查：

- card_cache 数据落库；
- Portal 查询条件；
- 卡片刷新机制。

### init 流程优化

当前目标流程：

```
init
 ↓
初始化working卡片
 ↓
展示已有TR
 ↓
用户选择是否新增TR
 ↓
重新执行init刷新TR关系
```

### 测试因子自动关联

目标：建设独立因子关联能力：

```
factor_code
      ↓
factor resolver
      ↓
factor_id
      ↓
TS关联
```

当前方案方向：

- 不直接依赖叶子 factor_id；
- 增加因子解析工具；
- 通过因子编码完成自动关联。

## 6. 重要约束

Skill 统一使用：

```
coretest-init
coretest-explore
coretest-design
coretest-archive
```

MCP：

```
127.0.0.1:8765
```

协议：

```
SSE
```

设计原则：

- 使用已有 Skill 扩展能力，不重复建设流程；
- 保持输入输出兼容；
- 修改 Skill 前确认上下游依赖；
- 每次重大修改同步更新文档。

## 7. 后续开发原则

1. 优先基于当前 Skill 架构演进。

2. 修改前：

- 阅读当前 SKILL.md；
- 明确输入输出；
- 验证上下游调用关系。

3. 保持版本演进可追踪。

4. 新对话启动时优先读取：

```
docs/PROJECT_CONTEXT.md
```

## 8. 下一步任务

优先级：

1. 排查 Portal 卡片缓存与展示链路；
2. 完成 init working 卡片与 TR 提示顺序优化；
3. 完善测试因子自动关联工具；
4. 持续完善 coretest-spec-e2e 0.2.x 能力。