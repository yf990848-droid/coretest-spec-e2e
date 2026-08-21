# TP/TC 平台写入数据格式规则

> 本文件定义 `ts_<NN>_test_design.md` 与 `ts_<NN>_test_cases.md` 末尾固定表格区的格式，供 `build_tp_tc_json.py` 读取生成 JSON。固定表格区格式不得手动改动。展开方法与 tpType/tpSourceType 取值见 `tp-tc-design-logic.md`；表格内容应与前段叙述保持一致。

## 填写规则

- 平台真实 id（tsId/parentTrId）统一填 `<PENDING>`，由脚本还原为占位串
- 可从分析或 `tp-tc-design-logic.md` 取值表得出的内容须填实值，不填 `<PENDING>`；无对应值时留空
- 多条编号列表（preparation/test_step/expect_output）：条目之间用 `<br>` 连接并保留编号，如 `1. xxx<br>2. yyy`
- 多值字段（raw_factors）：以英文逗号分隔，不留空格，如 `TFA-001,TFD-001`

### 在线文档固定标题

`ts_<NN>_test_design.md` 的叙述区必须按当前 TS 适用维度使用以下固定二级标题，标题文字不得改写，且每个标题下必须有非空正文：

- `## 功能交互设计`
- `## 基于业务场景的设计`
- `## 测试类型交互设计`
- `## 基于业务内部实现的设计`

具体 TS 应包含哪些标题，以 `tp-tc-design-logic.md` 的类型映射为准；禁止补写当前 TS 不适用的标题。

### 测试用例上报字段

每条 TC 必须生成 `TestType`、`AutoType`、`envtype`、`DesignNote`，不得填写 `<PENDING>`。

- `TestType`：根据用例验证目标从下表选择编码；无法识别时填字符串 `1`
- `AutoType`：明确为自动化用例时填字符串 `1`；明确为非自动化用例或无法识别时填字符串 `0`
- `envtype`：当前留空；该规则保留在本文件中，后续可按平台取值要求调整
- `DesignNote`：根据用例测试目的和验证内容生成一句简洁描述，不得留空、不得直接复制用例名称；不得包含 `|`，如需换行使用 `<br>`

#### TestType 取值映射

| 编码 | 测试类型 |
|---|---|
| 1 | 功能性-功能正确性 |
| 78 | 功能性-功能交互 |
| 3 | 功能性-协议一致性 |
| 90 | 性能-网络性能 |
| 4 | 性能-性能规格 |
| 88 | 性能-资源效率 |
| 25 | 性能-能耗 |
| 89 | 性能-业务服务质量 |
| 71 | 可靠性-可用性 |
| 87 | 可靠性-容错容灾 |
| 7 | 可靠性-耐力 |
| 91 | 可靠性-过载 |
| 9 | 可靠性-恢复 |
| 6 | 可靠性-压力 |
| 22 | 可靠性-业务级可靠 |
| 23 | 易用性-全球化 |
| 15 | 易用性-用户体验 |
| 19 | 兼容性-互通 |
| 2 | 兼容性-配套兼容性 |
| 14 | 安全性-安全遵从性 |
| 72 | 安全性-隐私 |
| 70 | 安全性-韧性 |
| 92 | 安全性-抗攻击性 |
| 83 | 可服务性-可部署性 |
| 16 | 可服务性-可维护性 |
| 21 | 可服务性-可定位性 |
| 5 | 其他-缩放测试 |
| 8 | 其他-配置测试 |
| 10 | 其他-故障注入测试 |
| 11 | 其他-安装测试 |
| 12 | 其他-流控测试 |
| 13 | 其他-备份测试 |
| 17 | 其他-QoS测试 |
| 18 | 其他-网络拓扑测试 |
| 20 | 其他-稳定性测试 |
| 24 | 其他-信息测试 |
| 26 | 其他-QOE测试 |
| 75 | 其他-耐力测试（待整改） |

---

## 元信息小表（`ts_<NN>_test_design.md` 末尾，置于 TP 表之前）

> TS 级元信息（tr_name/ts_name/ts_type）由本小表提供，脚本按行名读取，写入 tp.json 与 tc.json 的顶层字段。
> 元信息仅在 design md 中定义一份；cases md 不重复，脚本生成 tc.json 时从同一 TS 的 design md 读取。
> 本小表为固定格式，按行名定位，不依赖前段叙述区的措辞。

~~~markdown
## 平台写入数据 - 元信息

> 本章为固定格式，由 build_tp_tc_json.py 读取，请勿手动改动。

| 字段 | 值 |
|---|---|
| tr_name | 【中国移动】AM PCF支持NWDAF质差保障联动UE Logo显示-5GC-UPCF |
| ts_name | 数据层订阅通知配置验证 |
| ts_type | function |
~~~

| 行 | 说明 |
|---|---|
| `tr_name` | 所属 TR 名称，全 TR 唯一，取自 tr_ts.json 的 tr.tr_name，逐字填入 |
| `ts_name` | 本 TS 名称，与 tr_ts.json 中该 TS 的 ts_name 一致 |
| `ts_type` | 本 TS 类型，如 function/scene/constraint/performance 等 |

---

## TP 表（`ts_<NN>_test_design.md` 末尾，元信息小表之后）

~~~markdown
## 平台写入数据 - TP

> 本章为固定格式，由 build_tp_tc_json.py 读取，请勿手动改动。

| tp_id_temp | tpName | description | resolveDescription | rank | tsId | parentTrId | tpType | tpSourceType | requirement_ids | dimension | raw_factors |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TP.01.01.01 | N5专载建立正常订阅 | NWDAF建立N5专载，PCF正常接收订阅请求 | | 1 | <PENDING> | <PENDING> | BusinessSceneAnalysis | 基于业务场景设计—场景因子 | | 基于业务场景 | TFA-N5SUB-001,TFD-SESSION-001 |
| TP.01.03.01 | N5接口与PGW lib交互 | N5接口消息传递给PGW lib | | 2 | <PENDING> | <PENDING> | RequirementAnalysis | 功能交互设计-功能与测试因子 | | 功能交互设计 | TFA-IFACE-001 |
~~~

| 列 | 说明 |
|---|---|
| `rank` | Level 数字部分（Level1→1） |
| `resolveDescription` / `requirement_ids` | 当前阶段不产出，留空 |
| `tsId` / `parentTrId` | 平台 id，统一填 `<PENDING>` |
| `tpType` / `tpSourceType` | 按 `tp-tc-design-logic.md` 依 dimension 填非空实值，不得填写 `<PENDING>` 或留空 |
| `dimension` | 仅限：基于业务场景 / 基于业务内部实现 / 功能交互设计 / 测试类型交互设计 |

以下字段不写入表格，由编排层在生成 JSON 时注入：`designTaskId`、`creator`。

---

## TC 表（`ts_<NN>_test_cases.md` 末尾）

~~~markdown
## 平台写入数据 - TC

> 本章为固定格式，由 build_tp_tc_json.py 读取，请勿手动改动。

| tc_id_temp | tp_id_temp | name | rank | preparation | test_step | expect_output | case_id | TestType | AutoType | envtype | DesignNote |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TC.01 | TP.01.01.01 | [0101]N5专载建立正常订阅 | 1 | 1. PCF正常运行<br>2. NWDAF已配置 | 1. NWDAF发起订阅<br>2. PCF处理 | 1. 订阅成功<br>2. 记录创建 | PCF_N5SUB_01_01 | 1 | 0 | | 验证NWDAF发起N5专载订阅后PCF能够正确处理并创建订阅记录 |
~~~

| 列 | 说明 |
|---|---|
| `tp_id_temp` | 所属 TP 的编号，用于关联引用 |
| `case_id` | 完整用例编号，脚本据此派生 case_id_prefix（去除末尾 `_NN_NN`）、start_value（0）、number（1） |
| `TestType` | 按本文件 TestType 映射生成，无法识别时填 `1` |
| `AutoType` | 自动化填 `1`；非自动化或无法识别填 `0` |
| `envtype` | 当前留空，后续可在本文件中调整生成规则 |
| `DesignNote` | Agent 根据测试目的和验证内容生成的一句简洁设计描述 |

> tc.json 顶层的 tr_name/ts_name/ts_type 不在本表，由同一 TS 的 design md 中「平台写入数据 - 元信息」小表提供。

以下字段不写入表格，由编排层在生成 JSON 时注入：`creator`、`auto_type`(0)、`owner`(空)、`tp_id`/`tr_id`(TODO 占位)。其中小写 `auto_type` 属于 Archive 的 `create_tc` 链路，与本表用于卡片上报的 `AutoType` 无关。
