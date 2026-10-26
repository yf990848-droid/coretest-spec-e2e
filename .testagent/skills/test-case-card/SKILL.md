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

## 执行任务流程
使用`todowrite`工具，记录按序执行以下三步的每一步，不得遗漏或跳过、乱序
- 保存用例为json
- 校验生成的json格式
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
  - 使用python工具执行这个skill下的card_generate.py，有3个入参，${脚本输入参数input}，这个入参是一个json字符串。
  - 这个原始json有三个key：json_file_path
    - json_file_path：使用生成的测试用例的json文件，`.design_output/{需求编号}/json_file/test_case.json` 注意使用绝对路径
    - spec_info: 测试规格文档绝对路径：`{工作目录}/.design_output/{需求编号}/test_design_spec/{需求编号}_test_spec.md`
    - cida_info: CIDA信息对象json文件绝对路径：`.design_output/{需求编号}/json_file/cida_info.json`
  - 执行命令: 
    - **重要**：必须先cd到脚本的目录，然后使用python -u card_generate.py执行，不要直接使用绝对路径调用python脚本
    ```bash
    cd .testagent/skills/test-case-card/scripts;
    python -u card_generate.py "json_file_path" "spec_info" "cida_info"
    ```
  - 脚本执行示例：
  ```bash
   cd .testagent/skills/test-case-card/scripts;
   python -u card_generate.py "D:\\software\\testagent\\templates\\testagent-e2e-default@0.0.4\\testagent-e2e-default\\.design_output\\IR20260611000764\\json_file\\test_case.json" "D:\\software\\testagent\\templates\\testagent-e2e-default@0.0.4\\testagent-e2e-default\\.design_output\\IR20260611000764\\test_design_spec\\IR20260611000764_test_spec.md" "D:\software\testagent\templates\testagent-e2e-default@0.0.4\testagent-e2e-default\.design_output\IR20260611000764\json_file\cida_info.json"
  ```
 - 调用不成功时可以重试，直到调用成功，不可跳过，可以通过`.testagent/skills/test-case-card/scripts/card_generate.log`定位问题，重试时也需要遵循上面的规则，使用两个命令执行

## 注意事项
1. 调用脚本生成卡片必须执行，卡片状态更新为已完成
