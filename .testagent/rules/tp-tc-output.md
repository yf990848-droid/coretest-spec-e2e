# TP/TC 平台写入数据格式规则

> 本文件定义 `ts_<NN>_test_design.md` 与 `ts_<NN>_test_cases.md` 末尾固定表格区的格式，供 `build_tp_tc_json.py` 读取生成 JSON。固定表格区格式不得手动改动。展开方法与 tpType/tpSourceType 取值见 `tp-tc-design-logic.md`；表格内容应与前段叙述保持一致。

## 填写规则

- 平台真实 id（tsId/parentTrId）统一填 `<PENDING>`，由脚本还原为占位串
- 可从分析或 `tp-tc-design-logic.md` 取值表得出的内容须填实值，不填 `<PENDING>`；无对应值时留空
- 多条编号列表（preparation/test_step/expect_output）：条目之间用 `<br>` 连接并保留编号，如 `1. xxx<br>2. yyy`
- 多值字段（raw_factors）：以英文逗号分隔，不留空格，如 `TFA-001,TFD-001`

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
| TP.01.01.01 | N5专载建立正常订阅 | NWDAF建立N5专载，PCF正常接收订阅请求 | | 1 | <PENDING> | <PENDING> | BusinessSceneAnalysis | | | 基于业务场景 | TFA-N5SUB-001,TFD-SESSION-001 |
| TP.01.03.01 | N5接口与PGW lib交互 | N5接口消息传递给PGW lib | | 2 | <PENDING> | <PENDING> | RequirementAnalysis | 功能交互设计-功能上测试因子 | | 功能交互设计 | TFA-IFACE-001 |
~~~

| 列 | 说明 |
|---|---|
| `rank` | Level 数字部分（Level1→1） |
| `resolveDescription` / `requirement_ids` | 当前阶段不产出，留空 |
| `tsId` / `parentTrId` | 平台 id，统一填 `<PENDING>` |
| `tpType` / `tpSourceType` | 按 `tp-tc-design-logic.md` 依 dimension 填实值；维度1/2 的 tpSourceType 留空 |
| `dimension` | 仅限：基于业务场景 / 基于业务内部实现 / 功能交互设计 / 测试类型交互设计 |

以下字段不写入表格，由编排层在生成 JSON 时注入：`designTaskId`、`creator`。

---

## TC 表（`ts_<NN>_test_cases.md` 末尾）

~~~markdown
## 平台写入数据 - TC

> 本章为固定格式，由 build_tp_tc_json.py 读取，请勿手动改动。

| tc_id_temp | tp_id_temp | name | rank | preparation | test_step | expect_output | case_id |
|---|---|---|---|---|---|---|---|
| TC.01 | TP.01.01.01 | [0101]N5专载建立正常订阅 | 1 | 1. PCF正常运行<br>2. NWDAF已配置 | 1. NWDAF发起订阅<br>2. PCF处理 | 1. 订阅成功<br>2. 记录创建 | PCF_N5SUB_01_01 |
~~~

| 列 | 说明 |
|---|---|
| `tp_id_temp` | 所属 TP 的编号，用于关联引用 |
| `case_id` | 完整用例编号，脚本据此派生 case_id_prefix（去除末尾 `_NN_NN`）、start_value（0）、number（1） |

> tc.json 顶层的 tr_name/ts_name/ts_type 不在本表，由同一 TS 的 design md 中「平台写入数据 - 元信息」小表提供。

以下字段不写入表格，由编排层在生成 JSON 时注入：`creator`、`auto_type`(0)、`owner`(空)、`tp_id`/`tr_id`(TODO 占位)。
