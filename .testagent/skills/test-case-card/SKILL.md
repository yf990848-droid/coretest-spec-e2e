---
name: test-case-card
description: 复用已有单 TS 测试用例 JSON，更新对应的测试用例卡片
metadata:
  author: Data Storage Team
  version: "4.0"
---

# 测试用例卡片生成skill
## 概述
使用调用方提供的单 TS 测试用例 JSON、测试规格、CIDA 信息和初始化 key，调用脚本更新卡片。JSON 转换由 test-case-card-adapter 负责。

## E2E 入口：已有单 TS JSON 更新

由 `test-case-card-adapter` 调用，或用户要求更新已生成的 TS 卡片时，直接复用
`.design_output/<design_task_id>/TR_<tr_id>/ts_<NN>_test_case.json`，
不重新生成或修复 JSON，不导出 Excel，保留 adapter 已生成的全部字段。

执行前检查 JSON、规格文件、当前 TR 的 cida_info.json 均存在，并检查
`<root>/.testagent/skills/card-initializer/scripts/test_case/<requirement_id>_<ts-id>_card_id.txt`
存在且去除空白后非空。缺失或为空时返回失败，不依赖脚本生成新 UUID。
直接按“调用脚本更新卡片”传入四个位置参数，并遵守以下执行约束。

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

## 调用脚本更新卡片

通过 Agent 终端工具直接执行，参数为独立的位置参数，不是一个 JSON 字符串：

1. `json_file_path`：当前测试用例卡片 JSON 的绝对路径；E2E 使用 adapter 生成的单 TS 文件。
2. `spec_info`：调用方传入的测试规格文件绝对路径。
3. `cida_info`：CIDA 文件绝对路径；E2E 必须使用当前 TR 目录中的 cida_info.json，只读，不回退到旧配置。
4. `requirement_number_override`：E2E 必传 `<requirement_id>_<ts-id>`，与初始化 key 完全一致。

E2E 示例（PowerShell，同一次工具调用中的两条命令）：

```powershell
Set-Location -LiteralPath "<root>/.testagent/skills/test-case-card/scripts" -ErrorAction Stop
python -u card_generate.py "<root>/.design_output/<design_task_id>/TR_<tr_id>/ts_<NN>_test_case.json" "<spec-file>" "<cida-info>" "<requirement_id>_<ts-id>"
```

其他 Shell 按“卡片更新执行约束”调整切换目录语法，不嵌套启动 PowerShell。
失败时可查看本 Skill 的 `scripts/card_generate.log`，重试仍遵守相同调用方式及上层次数限制。

## 注意事项

调用脚本生成卡片不可跳过；按“卡片更新执行约束”核验原始返回，区分更新调用成功与页面实际展示。
