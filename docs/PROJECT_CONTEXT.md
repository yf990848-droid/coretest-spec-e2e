# CoreTest-spec-e2e 项目上下文

## 1. 项目目标

CoreTest-spec-e2e 是基于 TestAgent 的端到端智能测试设计能力扩展，目标是实现从需求输入到测试用例归档的自动化闭环：

```
需求 IR/SR
    ↓
coretest-init
    ↓
需求上下文初始化
    ↓
coretest-explore
    ↓
测试规格分析
    ↓
coretest-design
    ↓
测试点 TP / 测试用例 TC 设计
    ↓
test-case-card
    ↓
测试设计卡片展示
    ↓
coretest-archive
    ↓
TR / TS / TP / TC 自动归档
```

项目目标：
- 减少人工测试设计过程；
- 基于需求自动生成测试规格和测试用例；
- 自动关联测试对象；
- 自动完成测试资产归档。

## 2. 当前版本

当前版本：

```
coretest-spec-e2e 0.2.1
```

版本演进：

|版本|主要能力|
|-|-|
|0.1.x|打通需求探索、测试设计、卡片展示、归档基础流程|
|0.2.0|完善 E2E 测试设计流程，引入 TR/TS/TP/TC 自动化处理|
|0.2.1|优化 init 流程、支持 TR 关联需求输入、增强 explore 能力|

## 3. 核心能力

### coretest-init

能力：
- 根据产品版本获取设计任务；
- 获取 PBI、design_task、TR、IR/SR 关联关系；
- 初始化设计上下文。

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
- 多 SR 去重。

### coretest-design

每个 TS 输出：

```
ts_xx_test_design.md
ts_xx_test_cases.md
ts_xx_tp.json
ts_xx_tc.json
```

支持：
- TS 级并行设计；
- TP/TC 自动生成；
- 测试设计卡片初始化。

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
- 使用 archive_state.json 保存状态。

## 4. 当前验证状态

已完成验证：

- init 流程验证完成；
- explore 流程验证完成；
- design 流程验证完成；
- archive 基础流程验证完成。

示例：

```
IR:
IR20251206000098

TR:
3861

TS:
35792

TP:
18295
```

## 5. 当前待处理问题

### Portal 卡片显示问题

现象：

卡片接口返回成功，但 Portal 页面未显示。

需要排查：

- card_cache 是否落库；
- Portal 查询条件；
- 卡片刷新机制。

### init 流程优化

目标：

```
init
 ↓
创建 working 卡片
 ↓
展示已有 TR 信息
 ↓
提示是否新增 TR
```

### 测试因子自动关联

目标：设计独立因子关联工具：

```
factor_code
      ↓
factor resolver
      ↓
factor_id
      ↓
TS关联
```

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

## 7. 后续开发原则

1. 优先基于已有 Skill 修改，不重新设计流程。

2. 修改前：
- 阅读当前 SKILL.md；
- 确认输入输出；
- 保持版本兼容。

3. 每次重大修改更新 CHANGELOG.md。

4. 新对话启动时优先读取：

```
docs/PROJECT_CONTEXT.md
```

## 8. 下一步任务

优先级：

1. 修复 Portal 卡片显示问题；
2. 优化 init 卡片创建和 TR 提示顺序；
3. 完善测试因子自动关联方案；
4. 持续完善 0.2.x 版本。
