# 代码仓归档流程

> 适用于将已验证的 `coretest-spec-e2e` 扩展包变更，从本地模板目录归档到代码仓并合入目标分支。
> 本流程以 Windows PowerShell 为例，并以“脚本类 MR 的新增行数 + 删除行数不得超过 1000”为约束。

## 1. 目标与原则

代码仓归档的目标是将本地已验证版本完整、可审查地同步到代码仓，同时避免误提交运行环境配置、缓存和个人文件。

执行时遵循以下原则：

- 先同步远端目标分支，再复制本次确认过的文件；
- 只暂存明确属于本次版本的文件，不使用 `git add -A`；
- Python 等脚本文件按 MR 行数限制拆分；
- Markdown 文档可以集中到独立 MR；
- 多个 MR 串联时，后续分支必须基于前置 MR 合入后的最新目标分支创建；
- `.idea/`、`.opencode/`、本地 MCP 配置、运行日志和生成数据不归档；
- 提交前必须检查文件范围、变更行数和空白错误；
- 未确认的文件不恢复、不覆盖、不提交。

## 2. 示例目录与变量

以下路径仅为示例，归档新版本时替换版本号即可：

```powershell
$Version = "0.2.2"
$SourceRoot = "D:\TestAgent\templates\coretest-spec-e2e@$Version\coretest-spec-e2e"
$RepoRoot = "D:\CoreTestClaw_new"
$TargetBranch = "main"
```

进入代码仓：

```powershell
Set-Location -LiteralPath $RepoRoot
```

确认当前仓库和远端：

```powershell
git rev-parse --show-toplevel
git remote -v
git branch --show-current
git status -sb
```

## 3. 归档前检查

### 3.1 确认源版本

检查扩展包清单：

```powershell
Get-Content -LiteralPath (Join-Path $SourceRoot "codeagent-extension.json") -Raw -Encoding UTF8
```

重点确认：

- `name` 为 `coretest-spec-e2e`；
- `version` 与待归档版本一致；
- `description` 与本版本实际能力一致；
- WebApp 或脚本依赖包名时，包名和版本号已经同步更新。

### 3.2 保存当前工作区状态

```powershell
Set-Location -LiteralPath $RepoRoot
git status --short --untracked-files=all
git diff --name-status
```

如果工作区存在与本次归档无关的修改，不要执行 `git add -A`、`git restore .` 或其他批量命令。

### 3.3 同步目标分支

工作区中的未提交修改需要保留时，先确认切换分支不会覆盖同路径文件。然后同步远端：

```powershell
git fetch origin
git switch $TargetBranch
git pull --ff-only origin $TargetBranch
```

若目标分支不是 `main`，以实际归档分支为准。

## 4. 同步本次版本文件

优先使用明确文件清单复制，不要直接覆盖整个仓库。

示例：

```powershell
$Files = @(
    ".testagent/agents/coretest-init-agent.md",
    ".testagent/skills/coretest-init/SKILL.md",
    ".testagent/skills/test-init-context/SKILL.md",
    ".testagent/skills/test-init-context/scripts/generate_tr_context.py",
    "README.md",
    "codeagent-extension.json"
)

foreach ($RelativePath in $Files) {
    $SourcePath = Join-Path $SourceRoot $RelativePath
    $TargetPath = Join-Path $RepoRoot $RelativePath
    $TargetDir = Split-Path -Parent $TargetPath

    if (-not (Test-Path -LiteralPath $SourcePath)) {
        throw "源文件不存在：$SourcePath"
    }

    if (-not (Test-Path -LiteralPath $TargetDir)) {
        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    }

    Copy-Item -LiteralPath $SourcePath -Destination $TargetPath -Force
}
```

复制后立即检查：

```powershell
Set-Location -LiteralPath $RepoRoot
git status --short --untracked-files=all
git diff --name-status
git diff --stat
```

## 5. 排除不应归档的文件

以下内容通常属于本地环境，不应进入提交：

```text
.idea/
.opencode/
.opencode/mcp/mcp_settings.json
.testagent/mcp/mcp_settings.json
.testagent/AGENTS.md
.testagent/testagent.md
.design_output/
data/
logs/
*.log
.venv/
node_modules/
```

是否归档某个文件应以版本需求和仓库规范为准。对已有但不确定的修改，只保留在工作区并进一步确认，不要擅自删除。

可对目标路径进行精确检查：

```powershell
git status --short --untracked-files=all -- `
    ".testagent" `
    "README.md" `
    "codeagent-extension.json" `
    "docs"
```

## 6. 检查真实差异

### 6.1 查看文件和行数

```powershell
git diff --name-status
git diff --numstat --no-renames
git diff --check
```

`git diff --check` 无输出代表没有空白错误。以下提示通常只是换行符转换提醒，不等同于检查失败：

```text
LF will be replaced by CRLF the next time Git touches it
```

### 6.2 识别“假修改”

如果 `git status` 显示文件已修改，但 `git diff --exit-code` 返回 `0`，说明文件内容没有真实差异：

```powershell
git diff --exit-code -- ".testagent/mcp/core_test_design_mcp/mcp_server.py"
$LASTEXITCODE
```

仅当退出码为 `0` 时，可用暂存动作让 Git 重新计算该文件状态：

```powershell
git add -- ".testagent/mcp/core_test_design_mcp/mcp_server.py"
git status --short -- ".testagent/mcp/core_test_design_mcp/mcp_server.py"
git diff --cached --name-status -- ".testagent/mcp/core_test_design_mcp/mcp_server.py"
```

预期后两条无输出。若文件进入暂存区或存在实际差异，应停止并重新核对。

## 7. 按 MR 规则拆分

### 7.1 行数计算口径

脚本 MR 按“新增行数 + 删除行数”计算：

```powershell
$TotalChangedLines = 0

git diff --cached --numstat | ForEach-Object {
    $Columns = $_ -split "`t"
    if ($Columns[0] -match '^\d+$' -and $Columns[1] -match '^\d+$') {
        $TotalChangedLines += [int]$Columns[0] + [int]$Columns[1]
    }
}

$TotalChangedLines
```

脚本 MR 的结果必须小于 `1000`。拆成多个 commit 不能降低 MR 的总行数；超过限制时必须拆成多个分支和 MR。

### 7.2 推荐拆分方式

通常拆为两类：

| MR | 内容 | 约束 |
|---|---|---|
| 脚本 MR | `.py`、必要的代码文件 | 新增行数 + 删除行数 < 1000 |
| 文档 MR | Agent、Skill、README、docs 和版本清单 | 按团队文档规则执行 |

若单个脚本 MR 仍超过 1000 行，应继续按能力边界拆分，例如 Init、Explore、Design、Archive 分别提交。

## 8. 提交脚本 MR

### 8.1 创建分支

```powershell
git switch -c personal/<工号>/coretest-spec-e2e-<版本>-scripts
```

分支名中的版本可去掉点号，例如 `0.2.2` 写为 `022`。

### 8.2 精确暂存

示例：

```powershell
git add -- `
    ".testagent/skills/coretest-archive/scripts/archive_state.py" `
    ".testagent/skills/coretest-explore/scripts/file_download.py" `
    ".testagent/skills/test-init-context/scripts/generate_tr_context.py" `
    ".testagent/skills/test-spec-analysis/scripts/build_tr_json.py"
```

### 8.3 提交前核验

```powershell
git diff --cached --name-status
git diff --cached --numstat
git diff --cached --check
git status --short
```

确认：

- 暂存区只有计划内脚本；
- 总变更行数小于 1000；
- 没有空白错误；
- 本地配置和未跟踪文件没有进入暂存区。

### 8.4 提交和推送

```powershell
git commit -m "feat: adapt coretest scripts for <版本说明>"
git show --stat --oneline HEAD
git show --numstat --format="" HEAD
git push -u origin (git branch --show-current)
```

创建 MR 时填写：

- 源分支：当前脚本分支；
- 目标分支：`main` 或实际目标分支；
- 说明：本次脚本变更、影响范围和验证结果；
- 变更规模：文件数量及按上述口径计算的行数。

脚本 MR 合入后再继续文档 MR。

## 9. 提交文档 MR

### 9.1 基于最新目标分支创建分支

```powershell
git fetch origin
git switch -c personal/<工号>/coretest-spec-e2e-<版本>-docs origin/main
```

如果工作区保留了未提交文档修改，切换后再次确认脚本修改已经因前置 MR 合入而消失：

```powershell
git status -sb
git diff --name-status
```

### 9.2 精确暂存文档

示例：

```powershell
git add -- `
    ".testagent/agents/coretest-init-agent.md" `
    ".testagent/skills/coretest-init/SKILL.md" `
    ".testagent/skills/test-init-context/SKILL.md" `
    "README.md" `
    "docs/PROJECT_CONTEXT.md" `
    "codeagent-extension.json"
```

根据实际变更补充其他 Agent 或 Skill 文档，不要加入无关文件。

### 9.3 核验、提交和推送

```powershell
git diff --cached --name-status
git diff --cached --stat
git diff --cached --check
git status --short

git commit -m "docs: update CoreTest <版本> workflow"
git show --name-status --format="" HEAD
git push -u origin (git branch --show-current)
```

创建文档 MR，目标分支与脚本 MR 保持一致。

## 10. 合入后的最终检查

所有 MR 合入后：

```powershell
git fetch origin
git switch main
git pull --ff-only origin main
git status -sb
git log --oneline -5
```

核对关键文件：

```powershell
Get-Content -LiteralPath ".\codeagent-extension.json" -Raw -Encoding UTF8
Get-Content -LiteralPath ".\README.md" -TotalCount 30 -Encoding UTF8
Get-Content -LiteralPath ".\docs\PROJECT_CONTEXT.md" -TotalCount 30 -Encoding UTF8
```

最终确认：

- 版本号、描述和包名正确；
- 本次脚本与文档均已进入目标分支；
- 前置、后续 MR 没有遗漏依赖；
- 本地配置、缓存、日志和生成产物未进入仓库；
- 工作区剩余内容均为已知的个人文件或后续任务修改。

## 11. 常见问题

### 11.1 为什么不能只拆多个 commit？

MR 行数按源分支与目标分支的整体差异计算。一个 MR 中即使包含多个 commit，总差异仍会累计，因此超过限制时必须拆分支和 MR。

### 11.2 为什么后续 MR 要等待前置 MR 合入？

后续分支基于最新目标分支创建，可以让已经合入的脚本差异从工作区中自然消失，避免同一文件重复进入多个 MR。

### 11.3 LF/CRLF 警告需要处理吗？

仅出现 `LF will be replaced by CRLF` 时通常无需处理。以 `git diff --check` 是否报告真实空白错误为准，不要为了消除提示批量重写文件。

### 11.4 能否直接使用 `git add .`？

不建议。归档工作区通常包含个人配置、缓存和运行产物，应始终使用明确文件路径暂存。

### 11.5 发现不确定的已有修改怎么办？

停止暂存该文件，分别检查：

```powershell
git status --short -- "<文件路径>"
git diff -- "<文件路径>"
git diff --numstat -- "<文件路径>"
```

确认属于本次版本后再加入；不能确认时保留原状并向负责人核实。
