---
name: test-case-card
description: 负责转换测试用例为json和形成测试用例卡片
metadata:
  author: Data Storage Team
  version: "4.0"
---

# 测试用例卡片生成skill
## 概述
通过测试用例的文件`.design_output/{需求编号}/test_case_spec/{需求编号}_test_case_review.md`生成测试用例json和调用脚本生成卡片

## E2E 入口：已有单 TS JSON 更新

由 `test-case-card-adapter` 调用，或用户要求更新已生成的 TS 卡片时，直接复用
`.design_output/<design_task_id>/TR_<tr_id>/ts_<NN>_test_case.json`，
跳过下述旧流程的第一至第三步，不重新生成或修复 JSON，不导出 Excel。
保留 adapter 已生成的全部字段，不按旧示例裁剪。

执行前检查 JSON、规格文件、当前 TR 的 cida_info.json 均存在，并检查
`<root>/.testagent/skills/card-initializer/scripts/test_case/<requirement_id>_<ts-id>_card_id.txt`
存在且去除空白后非空。缺失或为空时返回失败，不依赖脚本生成新 UUID。
直接按第四步传入四个位置参数，并遵守以下执行约束。

## 卡片更新执行约束

- 必须通过 Agent 终端工具执行，每个 TS 使用一次独立的卡片更新工具调用。
- 同一次调用中先切换到本 Skill 的 scripts 目录，切换失败立即停止，再直接执行 `python -u card_generate.py`；不得从任意目录用脚本绝对路径替代。
- 命令按实际 Shell 编写：Bash 使用带引号的路径和正斜杠，PowerShell 使用 `Set-Location -LiteralPath "脚本目录" -ErrorAction Stop`，CMD 使用 `cd /d "脚本目录"`。两条命令在同一会话执行，不得假定上一次工具调用保留目录。
- 文件参数必须是带引号的绝对路径，展开为明确值；TS 更新的第四个参数必须与初始化 key 完全一致。
- 禁止使用 for/foreach、批量包装脚本、嵌套 Shell（如 powershell.exe -Command）执行卡片更新；禁止用 Shell 变量拼接参数。
- 禁止变量捕获、管道处理或重定向脚本输出；保留原始 JSON 返回，不添加 Shell 汇总输出。
- 多个 TS 逐张独立调用，不合并为一条批量命令；不同 TS Agent 仍可按上层并发限制各自独立调用。
- 示例中的 python 应使用上层已确认的 Python 解释器；使用解释器绝对路径时仍须进入脚本目录并以 card_generate.py 相对文件名直接执行。
- 检查进程退出码及原始返回：只有退出码为 0、`success=true` 且 `data.card_cache_id` 非空才能判定更新调用成功。脚本失败分支可能返回退出码 0，不得仅凭退出码或输入 JSON 文件存在判成功。
- 接口成功只代表缓存调用成功；未确认页面展示时不得宣称卡片已显示。
- 失败保留原始错误，按上层重试策略处理；本 Skill 不自行无限重试。E2E 流程遵循 test-design-agent 的最多一次重试；独立调用未指定重试策略时返回失败。

## 旧入口：从需求级 Markdown 生成

仅在未提供已有单 TS JSON、且明确要求从需求级 Markdown 生成时执行以下完整流程。

## 执行任务流程
使用`todowrite`工具，记录按序执行以下四步的每一步，不得遗漏或跳过、乱序
- 保存用例为json
- 校验生成的json格式
- 输出excel
- 调用脚本生成卡片

### 第一步：保存用例为json
- 将所有的测试用例`.design_output/{需求编号}/test_case_spec/{需求编号}_test_case_review.md`，生成到一份结构化的JSON数据，测试用例的json中要包含测试点与测试用例的对应关系
根对象只能包含以下 5 个字段, 不得包含任何其他字段。：
- title
- saved_file_path
- test_case_count
- test_point_count
- test_point_list

输出结构必须是：
```
{
    "title": "需求标题",
    "saved_file_path": "{下一步要保存的测试用例Excel文件的绝对路径}",
    "test_case_count": 1,
    "test_point_count": 1,
    "test_point_list": [
        {
            "name": "测试点名称",
            "number": "TP-007",
            "type": "",
            "description": "",
            "requirement_source": "扩展场景4：特性正交：",
            "test_case_list": [
                {
                    "name": "测试点下测试用例的名称",
                    "priority": "",
                    "number": "",
                    "type": "",
                    "pre": "",
                    "test_step": "",
                    "expect_output": ""
                }
            ]
        }
    ]
}
```
#### 字段约束
- 严禁使用旧版字段
- title：需求标题。
- saved_file_path：下一步要保存的测试用例 Excel 文件的绝对路径。
- test_case_count：所有测试用例总数，必须是整数。
- test_point_count：测试点总数，必须是整数。
- test_point_list：测试点列表，必须是数组。
- test_point_list.test_case_list：每个测试点下的测试用例列表，必须是数组。
- test_point_list.test_case_list.test_step：每个测试步骤以换行分隔。
- 没有内容的字符串字段填 ""。
- 没有内容的数组字段填 []。
- 数量为 0 时填 0，测试用例和测试点的数量要是真实数量
- 注意保证json格式正确，不出现引号嵌套等问题
- 测试用例json文件位置： `.design_output/{需求编号}/json_file/test_case.json`

最终输出前自行检查，但不要输出检查过程：

1. 根对象是否只有 title、saved_file_path、test_case_count、test_point_count、test_point_list。
2. 是否不存在 test_cases 字段。
3. 是否不存在 case_id、case_name、pre_condition、test_operation、expected_result 字段。
4. 每个测试点是否都放在 test_point_list 中。
5. 每个测试用例是否都放在 test_point_list[].test_case_list 中。
6. test_case_count 是否等于所有 test_case_list 的用例总数。
7. test_point_count 是否等于 test_point_list 的数量。
8. 最终输出是否只有 JSON。


### 第二步：校验生成的json格式
- 调用`./scripts/repair_json_tool.py`校验&修复JSON格式
    ```bash
    cd .testagent/skills/test-point-generator/scripts
    python -u repair_json_tool.py json文件路径
    ```
- 校验生成的`.design_output/{需求编号}/json_file/test_case.json`格式与示例：`./references/test_case_demo.json`，一致，如不满足需按目标格式修改

### 第三步：输出excel
- 将检视后的所有测试用例信息通过Python脚本转换为Excel格式
- 使用脚本 `json_to_excel.py`，该脚本位于 `.testagent/skills/test-case-reviewer/scripts/` 目录下
- 保存Excel文件到 `{工作目录}/.design_output/{需求编号}/excel_file/test_case.xlsx`
- 脚本调用方式（使用绝对路径）：
  ```bash
  cd .testagent/skills/test-case-reviewer/scripts
  python json_to_excel.py -input "{JSON文件绝对路径}" -output "{Excel输出文件绝对路径}"
  ```
- 调用示例：
  ```bash
  cd D:\code\ai_for_test\test-design\.testagent\skills\test-case-reviewer\scripts
  python json_to_excel.py -input "D:/code/ai_for_test/test-design/.design_output/{需求编号}/json_file/test_case.json" -output "D:/code/ai_for_test/test-design/.design_output/{需求编号}/excel_file/test_case.xlsx"
  ```

### 第四步：调用脚本生成卡片

通过 Agent 终端工具直接执行，参数为独立的位置参数，不是一个 JSON 字符串：

1. `json_file_path`：当前测试用例卡片 JSON 的绝对路径；E2E 使用 adapter 生成的单 TS 文件。
2. `spec_info`：调用方传入的测试规格文件绝对路径。
3. `cida_info`：CIDA 文件绝对路径；E2E 必须使用当前 TR 目录中的 cida_info.json，只读，不回退到旧配置。
4. `requirement_number_override`：E2E 必传 `<requirement_id>_<ts-id>`，与初始化 key 完全一致；旧需求级入口可省略，此时脚本从 CIDA 读取需求编号。

E2E 示例（PowerShell，同一次工具调用中的两条命令）：

```powershell
Set-Location -LiteralPath "<root>/.testagent/skills/test-case-card/scripts" -ErrorAction Stop
python -u card_generate.py "<root>/.design_output/<design_task_id>/TR_<tr_id>/ts_<NN>_test_case.json" "<spec-file>" "<cida-info>" "<requirement_id>_<ts-id>"
```

其他 Shell 按“卡片更新执行约束”调整切换目录语法，不嵌套启动 PowerShell。
失败时可查看本 Skill 的 `scripts/card_generate.log`，重试仍遵守相同调用方式及上层次数限制。

## 注意事项

调用脚本生成卡片不可跳过；按“卡片更新执行约束”核验原始返回，区分更新调用成功与页面实际展示。
