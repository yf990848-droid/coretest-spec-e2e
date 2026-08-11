---
compatibility: Works without npm - 需要 pandoc 命令行工具
description: CoreTest Explore 测试侧需求探索 SKILL - 完成从需求 ID
  或本地 .docx 到测试规格（test_specs）的全流程产出。内置 CoreAlm
  需求获取与文档下载能力，调用
  spec-extractor、requirement-parser、test-spec-analysis 三个下游
  Skill，生成测试规格及 tr_ts.json。服务 TSE
  业务方完成需求理解、测试策略分析和测试规格分解。
license: MIT
metadata:
  author: corespec
  generatedBy: manual
  version: 0.3
name: coretest-explore
---

# CoreTest Explore - 测试侧需求探索与测试规格生成助手

## 1. 功能定位

本 SKILL 是测试侧需求探索的核心 Skill，完成从需求到测试规格的全流程：

1.  获取 CoreAlm 需求信息并下载需求文档
2.  `spec-extractor`：从 .docx 抽取生成《系统需求.md》和《功能设计.md》
3.  `requirement-parser`：以 .docx
    为主输入，结合《系统需求.md》和《功能设计.md》辅助校验与分摊，按 SR
    拆分生成 sr_specs/
4.  `test-spec-analysis`：遍历全部 SR，按 IR↔TR 一对一生成测试规格及 TS

本 SKILL 负责统一组织整个测试需求探索流程，包括需求获取、文档下载、下游
Skill 调用、阶段控制、用户确认及错误处理。

## 2. 输入要求

用户需要提供以下信息之一:

-   **TR ID**:测试设计TR ID（如 3867），用于从初始化上下文中定位已有TR及关联需求。
-   **需求 ID**:US 号(如 US20251017596178)、Story
    号(ST20251017596178)、SR 号(SR20260110000656)、IR
    号(IR20251125001262)
-   **本地 .docx 路径**:已下载到本地的需求文档绝对路径(如
    D:/docs/req.docx)
-   **自由描述**:对需求的自然语言描述(如 "Logo 联动保障")

可选标志:

-   `--skip-clarify`:跳过确认点,连续完成后续流程
-   `--function-numbers <编号>`:平台功能编号(逗号分隔)。阶段 6
    注入给下游,由其写入测试规格 md 后段 TR 表的 `function_numbers`
    字段。设计任务模式下优先从 `.design_output/design_task_info.json`
    根据 `design_task_id` 自动获取
    `function_list[].function_number`;若未获取到且用户未传入,
    则下游填占位值 `<PENDING-coretest-init>`。(注意:本参数不传给阶段 6.5
    的脚本------脚本从 md 提取该值。)
-   `--design-task-id <dtId>`:CloudSpider 页面的设计任务 ID(dtId)。写入
    TR 平台时必需,透传至阶段 6.5 提取脚本的 `--design-task-id`
    参数;未传则在阶段 6.5 写平台前停下询问用户,不得编造或留空。

## 3. 执行模式

本 SKILL 采用 **AI 自主判断**
的执行模式,而非固定脚本流水线。每个阶段执行后,依据当前状态判断下一步:

-   可通过 Bash 工具调用脚本(用于 pandoc 可用性检查、阶段 6.5 组装脚本)
-   通过 OpenCode 的 Skill 调用机制依次调用 3 个下游 Skill
-   可使用 Read/Write/Edit 工具读写文件
-   可依判断结果决定是否跳过某些阶段

执行各阶段时须使用 `todowrite`
工具创建并跟踪任务,确保每阶段被执行与验证。门面 Skill 跟踪门面级 todo(8
个阶段,含阶段 6.5),各下游 Skill 维护各自内部
todo,两层互不干扰。任务完成后更新状态为
`completed`,每阶段执行后输出进度信息。

## 4. 工作流程与判断节点

### 阶段 0:Context Gathering(启动前必做检查)

**动作**:在进入任何后续阶段前,执行以下检查:

1.  **读取目标仓的 AGENTS.md 或 aw_development_guide.md**(若存在)
    -   提取命名规范、目录约定、文档风格要求
    -   将上述约束作为后续所有产出的硬约束注入
2.  **列出 `corespec/changes/` 已有变更**
    -   用户可能在已有变更上追加,而非新建
    -   若已存在 `test-<需求id>-*` 目录,询问用户:覆盖重做 / 增量补做 /
        取消
3.  **检查 pandoc 命令是否可用**:通过 Bash 调用 `pandoc --version`

**判断**: - pandoc 缺失 → 报错并退出,给出安装提示: - Windows:
`winget install --id JohnMacFarlane.Pandoc` - Linux:
`apt install pandoc` - macOS: `brew install pandoc` -
变更目录已存在且用户选择"取消" → 退出 - 全部通过 → 进入阶段 1

### 阶段 1:模式判断

**动作**:根据用户输入第一参数判断执行模式:

  ---------------------------------------------------------------------------------------
  输入特征               模式             下一阶段
  ---------------------- ---------------- -----------------------------------------------
  匹配纯数字             模式 C（设计任务 阶段 2
  design_task_id（如     ID）             
  `2470`）                                

  匹配                   模式 B（需求     阶段 2
  `^(IR|SR|US|ST)\d+$`   ID，兼容模式）   

  以 `.docx` 结尾的路径  模式 B（本地     阶段
                         .docx）          3（直接生成《系统需求.md》和《功能设计.md》）

  其他非空字符串         模式             阶段 1.A
                         A（自由描述）    

  缺省                   模式 A           阶段 1.A（提示用户输入）
  ---------------------------------------------------------------------------------------

**判断**:按上表分发,进入对应阶段。

### 阶段 1.A:模式 A - 对话式探索(仅模式 A 进入)

**动作**:对话式澄清，目标是补全测试范围，而不是直接生成完整产物。

1.  **接收并消化输入**:若用户未提供任何描述，提示其输入需求、疑问或场景片段
2.  **多轮澄清**:围绕以下维度提问(按需选取，不必每次问全):
    -   涉及的产品 / 模块 / 网元
    -   测试范围边界
    -   验收标准 / 关键观察点
    -   是否有可参考的设计文档、历史用例、已有测试规格
    -   是否有需求 ID 或本地 Word 文档，便于转入模式 B
3.  **决策分叉**:澄清到一定程度后，询问用户:
    -   **(a)** 转入模式 B:让用户提供需求 ID 或 Word
        文档路径，重新调用本 SKILL
    -   **(b)** 停在 explore:生成简化版需求沉淀，不走下游 Skill
    -   **(c)** 不产出:仅作为思考过程，不写文件

模式 A 的对话风格：好奇、不强加结构、跟随用户思路、必要时用简单 ASCII
图辅助说明。

**判断**: - 用户选 (a) → 用户重新调用本 SKILL，本次执行结束 - 用户选 (b)
→ 生成简化版需求沉淀文件，本次执行结束 - 用户选 (c) →
本次执行结束，不产出任何文件

### 阶段 2:获取需求信息并下载附件（模式 B）

执行内容：

1.  校验需求 ID。
2.  读取 `.design_output/design_task_info.json`，根据用户输入的
    `tr_id` 在 `data[].tr_list[]` 中定位已有TR信息，并获取当前用户工号。
    根据 TR 的 `ir_list[].requirement_type` 判断实际关联需求类型（IR/SR），使用实际需求编号继续后续流程。
    若兼容设计任务模式，则保持原有 `design_task_id` 定位逻辑。

3.  根据定位到的已有TR信息生成：

        .design_output/<design_task_id>/<requirement_id>/tr_context.json

    保存当前选择TR上下文，供后续 `test-spec-analysis` 阶段复用。
    文件内容来源于当前选择的TR，不重新生成TR。
    关联需求信息根据 `tr.ir_list[].requirement_type` 区分 IR/SR，目录和文档下载均使用实际 `requirement_id`。
3.  创建需求文档目录：

        .design_output/<design_task_id>/<requirement_id>/design_doc/

4.  调用 `scripts/corealm_api.py` 获取 CoreAlm 需求信息：

        cd .testagent/skills/coretest-explore/scripts
        python corealm_api.py --id "<requirement_id>" --user "<当前用户工号>"

5.  从返回结果中获取：
    -   description
    -   IR/SR/US 信息
    -   `doc_info[].doc_id`
    -   `doc_info[].doc_type`（支持 `DBOX`、`IDP`）
6.  基于 description 总结：
    -   change-name（英文，kebab-case）
    -   中文需求名
7.  从 `doc_info` 中选择有效文档。`doc_id` 不得为空，`doc_type`
    必须为 `DBOX` 或 `IDP`；若存在多个有效文档，优先选择与当前 IR
    对应且 introduction 最匹配需求描述的 Word 文档，无法判断时询问用户。
8.  调用 `scripts/file_download.py` 下载 Word 文档：

        cd .testagent/skills/coretest-explore/scripts
        python file_download.py --doc-id "<doc_id>" --output-dir ".design_output/<design_task_id>/<requirement_id>/design_doc" --us-num "<requirement_id>" --doc-type "<doc_type>"

9.  下载成功后，固定使用以下路径并检查文件确实存在：

        .design_output/<design_task_id>/<requirement_id>/design_doc/<IR编号>.docx

    将该绝对路径记录为 `docx_path`。不得根据旧文件或其他 `.docx`
    猜测下载结果，也不得在目标文件不存在时继续进入阶段 3。
10. 返回：
    -   docx_path
    -   change-name
    -   中文需求名

**判断**:

-   CoreAlm 查询失败 → 提示用户检查需求 ID 或网络，允许切回模式 A
-   `doc_info` 为空或没有有效 `doc_id` → 提示需求未关联可下载文档，允许改用本地
    `.docx`
-   `doc_type` 缺失或不是 `DBOX`/`IDP` → 停止下载并报告实际返回值
-   文档下载失败 → 提示用户检查附件、文档权限或改用本地 `.docx`
-   下载命令成功但固定路径文件不存在 → 判定下载失败，不进入阶段 3
-   成功 → 记录固定 `.docx` 路径、英文短名、中文需求名，进入阶段 3

**设计任务上下文提取**: 设计任务模式下读取
`.design_output/design_task_info.json`,根据 `design_task_id`
定位任务信息，并提取： - `feature_list[].feature_number` -
`function_list[].function_number`

作为后续测试规格生成阶段的平台写入数据上下文。

**输出目录创建**:基于 `design_task_id` 与 `requirement_number` 创建
`.design_output/<design_task_id>/<requirement_id>/`，例如
`.design_output/2470/IR20251206000098/`。

### 阶段 3:调用 spec-extractor

**Invoke**: `skills/spec-extractor`

**输入参数**: - `docx_path` = 阶段 2 的 .docx 路径(或用户直接提供的本地
.docx) - `output_dir` = `.design_output/<design_task_id>/<requirement_id>/`
绝对路径 - `source_id` = 需求 ID(或 .docx 文件名,若用户走本地分支) -
`author` = 当前用户工号 + `(via spec-extractor)`

**模式 B 本地 .docx 分支**:跳过阶段 2,直接以用户提供的 .docx
进入本阶段;英文短名与中文需求名由 AI 自 .docx
文件名或前几页内容总结;输出目录在本阶段开始时创建为
`.design_output/<design_task_id>/<requirement_id>/`。

**产物**:`系统需求.md`、`功能设计.md`(结构见 spec-extractor SKILL.md)。

**判断**: - spec-extractor 报错 → 报错退出(pandoc 已在阶段 0
检查,此处罕见) - spec-extractor 警告"抽不出有效内容" → 提示用户检查
.docx 质量,允许手工编辑后继续 - spec-extractor 成功 → 进入阶段 4

### 阶段 4:调用 requirement-parser

**Invoke**: `skills/requirement-parser`

**输入参数**: - 主输入：阶段 2/3 的 `.docx` 路径 - `output_dir` = 同阶段
3

requirement-parser 从 `.docx` 提取完整 IR/SR/US 分层结构，同时读取
`<output_dir>/系统需求.md`、`<output_dir>/功能设计.md`
作为辅助输入，用于交叉校验、补充字段和横切信息分摊。

**判断**: - `.docx` 缺失或不可读 → 中断 - `系统需求.md` 或 `功能设计.md`
缺失 → 警告但不中断 - requirement-parser 解析出 0 个 SR →
警告但不中断，提示人工补充 - requirement-parser 成功 → 进入阶段 5

### 阶段 5:显式停顿点

**动作**:向用户展示: - 需求结构概览(IR/SR 层次树 + SR 数量统计) -
产物路径:`系统需求.md` / `功能设计.md`(阶段 3)、`sr_specs/`(阶段 4) -
`_index.md` 中"未分摊横切信息"条目数(若不为 0,提示重点复核) -
提示:"需求结构与 SR 拆分是否符合预期？确认后将开始生成测试规格。"

**判断**: - 用户确认 → 进入阶段 6 - 用户要求修改 → 提示用户手工编辑
`sr_specs/` 下相关文件,完成后告知继续,再进入阶段 6 - 用户传入
`--skip-clarify` → 跳过本阶段,直接进入阶段 6

本 SKILL 默认包含两个显式停顿点：

-   阶段5：确认 SR 拆分结果
-   阶段6.1：确认测试规格 Markdown

传入 --skip-clarify 时可跳过上述确认点。

### 阶段 6:调用 test-spec-analysis

**Invoke**: `skills/test-spec-analysis`

**输入参数**: - 主输入:`<output_dir>/sr_specs/` 下全部 SR 文件(遍历
`sr_specs/*.md`,`_index.md` 作为 IR 信息与 SR 清单参考)

**TR 粒度与产物格式注入**(须显式告知下游 Skill):

> 1.  TR 来源:使用用户选择的已有 TR。测试规格生成时不得创建新的 TR。
>     各 SR 的测试内容挂载到该已有 TR 下。tr_ts.json 中 TR 字段保持原有结构，
>     数据来源为用户选择的 TR 信息。
> 2.  当前 TR 上下文文件：
>
>     `.design_output/<design_task_id>/<requirement_id>/tr_context.json`
>
>     该文件由本阶段生成，供 `test-spec-analysis` 读取已有 TR 信息。
> 2.  产物:下游产出唯一一份测试规格 md
>     `<中文需求名>测试规格.md`,含**前段**(自由分析过程,供人阅读)与**后段**(标题
>     `## 平台写入数据` 的固定格式章节,含 TR 表与 TS
>     清单表)。后段的内容规则(TS
>     四类定义、拆分原则、命名约定、描述模板、TR 段填法)以
>     `rules/ts-split.md` 为准,下游须读取并据此填写;格式骨架见
>     test-spec-analysis SKILL.md。**下游不生成任何
>     JSON**------写平台用的 JSON 由阶段 6.5 脚本从本 md 后段提取。
> 3.  function 编号:`function_numbers` 与 `feature_numbers`
>     由本阶段注入给下游写入后段 TR 表。设计任务模式下从
>     `.design_output/design_task_info.json` 自动获取：
>     -   `function_list[].function_number`
>     -   `feature_list[].feature_number` 若用户传入
>         `--function-numbers` 或 `--feature-numbers` 则优先使用。
>         未获取到 `function_numbers` 时填占位
>         `<PENDING-coretest-init>`，未获取到 `feature_numbers`
>         时保持为空。`design_task_id` 与 `creator` 不写入 md(由阶段 6.5
>         脚本补)。

**文件名提示**:产物落到 `<output_dir>/test_specs/`;`<中文需求名>`
取自阶段 2,`<IR编号>` 取自需求 ID。

**产物**:单产物落
`test_specs/`(`<中文需求名>测试规格.md`,含前段分析过程与后段
`## 平台写入数据` 固定章节)。写平台用的 `tr_ts.json`
不在本阶段产出,由阶段 6.5 脚本从该 md 后段提取。

**判断**: - test-spec-analysis 产出 0 个 TS →
警告并中断,提示检查输入文档质量后重跑 - test-spec-analysis 产出多于 1 个
TR → 警告,提示复核或重跑 - test-spec-analysis 成功 → 进入阶段 6.1

### 阶段 6.1：确认测试规格

**动作**：

向用户展示阶段 6 生成的测试规格 Markdown，并给出简要摘要，包括：

-   测试规格文件路径
-   TR 数量
-   TS 数量
-   各 TS 类型统计
-   测试范围概览

请先展示内容后，再让用户确认测试规格是否符合预期。

**判断**：

-   用户确认 → 进入阶段 6.5，生成 `tr_ts.json`
-   用户要求修改 → 根据反馈调整测试规格，重新执行阶段 6
-   用户传入 `--skip-clarify` → 跳过本阶段，直接进入阶段 6.5

### 阶段 6.5:从 md 提取 tr_ts.json 并写入 TR 平台

本阶段把写平台用的 JSON 交给确定性脚本**从阶段 6 的测试规格 md
后段提取**组装,再由 agent 原样调 create-tr MCP
写入。**全程不由模型生成或改写任何字段值**,以根除 JSON 格式不稳定。

**动作 1 --- 调脚本从 md 提取 JSON**:

通过 Bash 调用提取脚本:

    python <项目仓>/.opencode/skills/test-spec-analysis/scripts/build_tr_json.py \
      <output_dir>/test_specs/<中文需求名>测试规格.md \
      --design-task-id <dtId>

参数来源: - 第一个位置参数 = 阶段 6 产出的测试规格
md(`<output_dir>/test_specs/<中文需求名>测试规格.md`)。脚本只读其
`## 平台写入数据` 后段。 - `--design-task-id` = 用户运行
`/coretest-explore` 时透传的
`--design-task-id`。**若用户未传,在此停下询问用户,不得编造或填空**;沙盒环境取
281。 - creator 由脚本从环境变量 `USERNAME`
自取(平台认本人工号),不传参。 - `function_numbers`
不在此传参------它已由阶段 6 写入 md 后段 TR 表,脚本从 md 提取。

脚本产出落 `<output_dir>/test_specs/tr_ts.json`(默认与 md
同目录),屏幕仅打一句摘要(TS 条数 + 落点)。脚本只保证 JSON 形状合规(7
参数齐、可传 MCP),内容全部来自 md 后段。

**动作 2 --- 校验 JSON 产物**:

读取
`<output_dir>/test_specs/tr_ts.json`，确认文件已成功生成，并检查其中包含
`tr` 和 `test_specs` 数据结构。

记录 `tr_ts.json`
的生成路径，并将其作为本次需求分析流程的输出产物，用于后续测试设计和平台接入。

**判断**: - 脚本报错(`--design-task-id` 缺失 / md 缺 `## 平台写入数据`
锚点或 TR 字段未填 / TS 清单为空 / `USERNAME` 取不到) →
中断,向用户展示脚本报错原文,按提示补齐(多为回阶段 6 补填 md
后段)后重跑本阶段。 - `tr_ts.json` 未生成 → 中断。 - `tr_ts.json`
生成成功 → 进入阶段 7。

### 阶段 7:汇总与结束

**动作**:向用户输出执行汇总: - 模式判断结果(A/B/C) - 输出目录路径 -
产物文件路径(`<中文需求名>测试规格.md`、`tr_ts.json`) - TR JSON
生成结果 - 关键统计(IR 数 / SR 数 / TR 数=1 / TS 数)

后续提示: 测试规格已生成，可根据 TS 选择进入测试设计阶段。

单个 TS: `/coretest-design TS_01`

多个 TS: `/coretest-design TS_01 TS_02 TS_03`

不指定 TS: `/coretest-design`

由 coretest-design 默认执行全部 TS。

**判断**:本 SKILL 执行结束。

## 5. 下游 Skill 一览

  --------------------------------------------------------------------------------------------
  下游 Skill                    调用时机     输入
  ----------------------------- ------------ -------------------------------------------------
  `skills/spec-extractor`       阶段 3       docx_path, output_dir, source_id, author

  `skills/requirement-parser`   阶段 4       docx_path、系统需求.md、功能设计.md、output_dir

  `skills/test-spec-analysis`   阶段 6       sr_specs/ 全部 SR 文件 + TR 粒度与产物格式注入 +
                                             function_numbers 注入
  --------------------------------------------------------------------------------------------

各下游 Skill 的产物与内部细节(章节顺序、todowrite
步数、模板格式等)由其自身 SKILL.md 负责,本 SKILL 不干预。阶段 6 的 TR
粒度由本 SKILL 统一注入。

## 6. 输出目录

设计任务模式完整通过后,输出目录布局:

    .design_output/<design_task_id>/<requirement_id>/
    ├── design_doc/
    │   └── <requirement_id>.docx       (阶段 2)
    ├── 系统需求.md            (阶段 3)
    ├── 功能设计.md            (阶段 3)
    ├── sr_specs/             (阶段 4)
    └── test_specs/           (阶段 6 / 6.5)
        ├── <中文需求名>测试规格.md   (阶段 6,分析过程,供人阅读)
        └── tr_ts.json               (阶段 6.5,脚本组装,写平台用)

模式 A(用户选择"停在
explore")仅产需求沉淀文件,落地路径由用户在对话中指定。

## 7. 错误处理

  -----------------------------------------------------------------------------
  错误场景                   处理
  -------------------------- --------------------------------------------------
  pandoc 未安装              阶段 0 检测到后报错并退出,给出安装提示

  需求 ID 在 CoreAlm         阶段 2 报错,提示检查 ID 格式,提供切回模式 A 入口
  查询不到                   

  需求未关联文档或文档类型不  阶段 2 中断,展示 doc_info/doc_type 实际结果,提示检查
  是 DBOX/IDP                需求附件或改用本地 .docx

  下载完成但固定路径不存在    阶段 2 判定下载失败,不得进入阶段 3

  Word 文档不存在或无读权限  报错并退出,**不创建变更目录**

  Word 文档无附件可下载(需求 提示用户手工提供 `.docx` 路径,以本地分支重新调用
  ID 分支)                   

  spec-extractor             警告但不中断,提示检查 .docx
  抽不出有效内容             质量,允许手工编辑后继续

  requirement-parser 解析出  警告但不中断,提示人工补充
  0 个 SR                    

  requirement-parser         阶段 5 停顿点提示重点复核
  "未分摊横切信息"条目多     

  test-spec-analysis 产出 0  警告并中断,提示检查输入文档质量后重跑
  个 TS                      

  阶段 6.5 缺                停下询问用户补传,不编造、不留空,补齐后重跑本阶段
  `--design-task-id`         

  阶段 6.5 提取脚本报错(md   中断,展示脚本报错原文,按提示(多为回阶段 6 补填 md
  缺锚点 / TR 字段未填 / TS  后段)补齐后重跑;不进入写平台动作
  清单为空 / `USERNAME`      
  取不到)                    

  变更目录已存在且含         阶段 0 暂停并询问:覆盖 / 增量 / 取消
  test_specs/                

  任意下游 Skill 抛出        报错并退出,展示错误信息,不删除已生成的部分产物
  Exception                  
  -----------------------------------------------------------------------------

## 8. Guardrails

-   **输出目录隔离**:仅在 `.design_output/<design_task_id>/<requirement_id>/`
    下写文件
-   **不跳过停顿点**:除用户显式传入 `--skip-clarify` 外,阶段 5
    与阶段6.1均须等待用户确认
-   **JSON 由脚本从 md 提取**:写平台用的 `tr_ts.json` 一律由阶段 6.5
    的确定性脚本从测试规格 md 后段提取生成,下游 Skill 不得自行生成
    JSON;md 后段内容规则以 `rules/ts-split.md` 为准
-   **不约束下游其余内部行为**:除 TR 粒度外,不干预下游 Skill 的内部执行
-   **不重排调用顺序**:阶段 2 → 3 → 4 → 5 → 6 → 6.5
    为固定顺序,不并行、不乱序
-   **以 todowrite 跟踪门面级 8 个阶段(含阶段 6.5)**

## 9. 调用示例

### 模式 B - 需求 ID

    /coretest-explore 2470 --ir-id IR20251125001262

      阶段 0  Context Gathering          ✓ (pandoc 可用,无变更冲突)
      阶段 1  模式判断 → 模式 B 需求 ID    ✓
      阶段 2  获取需求并下载文档          ✓ (.docx + logo-trigger + Logo联动保障)
      阶段 3  spec-extractor             ✓ (系统需求.md + 功能设计.md)
      阶段 4  requirement-parser         ✓ (sr_specs/, 1 IR + 10 SR)
      阶段 5  显式停顿点                  ✓ (用户确认 SR 拆分)
      阶段 6  test-spec-analysis         ✓ (测试规格.md, 1 TR / 10 SR / N TS)
      阶段 6.1 测试规格确认               ✓ (用户确认测试规格)
      阶段 6.5 组装 TR JSON              ✓ (tr_ts.json 生成完成)
      阶段 7  汇总与结束                  ✓

    汇总：输出目录 .design_output/2470/IR20251125001262/；统计 IR=1，SR=10，TR=1，TS=N；
    测试规格已确认，TR JSON 已生成；下一步执行：
    /coretest-design TS_01

    或批量执行：
    /coretest-design TS_01 TS_02 TS_03

    或不指定 TS 执行全部：
    /coretest-design

### 模式 B - 本地 .docx

    /coretest-explore D:/docs/logo联动保障_需求说明书.docx --design-task-id 281

      阶段 2 跳过(无需 CoreAlm 拉取),其余同需求 ID 分支

### 模式 A - 自由描述

    /coretest-explore Logo 联动保障

      阶段 1.A 对话式探索 → 多轮澄清后用户选 (b) 停在 explore,生成需求沉淀文件
