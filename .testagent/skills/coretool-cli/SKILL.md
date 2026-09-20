---
name: coretool-cli
description: CoreTool CLI — 华为 CoreTool 平台开发者工具。当用户提到 CoreTool、CoreALM、需求查询、文档下载、W3 登录、coretool-cli、coretool 命令、CoreTest、InFactory、Script、Pipeline、TestResult、LCM、TestDesign、测试执行、测试结果、环境修复、测试设计、正交组合、资产库、场景、特性、功能、测试因子、模型、设计原则时使用此 skill。支持自然语言调用认证、需求搜索、文档下载、测试平台操作等。
---

# CoreTool CLI Skill

CoreTool CLI 是华为 CoreTool 平台的命令行工具，支持 W3 认证、需求查询、文档下载、测试平台操作等功能。

每次会话首次使用时从扩展包内确定 CoreTool CLI 的绝对路径并记为 `<coretool_cmd>`。后续命令及 references 中的 `coretool-cli` 仅表示命令名占位符，实际执行时必须替换为 `<coretool_cmd>`。

## References 路由表

根据用户意图读取对应领域参考文档：
- 需求查询 / 文档下载 → [references/corealm.md](references/corealm.md)
- 测试平台操作（InFactory、Script、Pipeline、TestResult、LCM、TestDesign） → [references/coretest.md](references/coretest.md)

## 环境准备

`<extension-root>` 是包含当前 `.testagent` 目录的扩展包根目录。Windows PowerShell 下只检查扩展包内置 CLI 的这一条路径：

```powershell
$CoreTool = Join-Path '<extension-root>' '.testagent\skills\coretool-cli\tools\coretool-cli.exe'
if (-not (Test-Path -LiteralPath $CoreTool -PathType Leaf)) {
    throw "CoreTool CLI 不存在：$CoreTool"
}
& $CoreTool version
if ($LASTEXITCODE -ne 0) { throw "CoreTool CLI version 校验失败：$CoreTool" }
& $CoreTool auth status
```

把通过校验的绝对路径记为 `<coretool_cmd>`。跨 shell 或跨工具调用时重新使用该绝对路径；找不到或校验失败时停止业务操作并报告。

本文及 references 中的 `coretool-cli` 命令均指此路径；PowerShell 中执行原生命令时使用 `& $CoreTool ...`。

## 认证

所有业务命令执行前需先登录。未登录时会提示 `not logged in. Run 'coretool-cli auth login' to authenticate`。

### W3 登录（个人账号，推荐）

交互式：
```bash
coretool-cli auth login
```

非交互式：
```bash
coretool-cli auth login -u <工号> -p <密码>
```

### Token 登录

交互式（安全，token 不进 shell history）：
```bash
coretool-cli auth login --token -u <工号>
```

非交互式（CI/脚本场景）：
```bash
coretool-cli auth login --token -u <工号> --auth-token <token>
```

注意：Token 登录不支持自动刷新，过期后需重新登录。

### 公共账号登录（服务账号 + 操作者）

当其他 CLI 工具以公共账号调用 coretool 时，用 `--service-account` 标记，并用 `--operator` 指定实际操作者工号：

```bash
coretool-cli auth login --token --service-account -u <公共账号> --auth-token <token> --operator <操作者工号>
```

- 公共账号模式下，业务命令使用操作者身份（工号、姓名、邮箱），而非公共账号身份
- 操作者身份也可通过环境变量 `CORETOOL_OPERATOR` 指定

### 查看登录状态

```bash
coretool-cli auth status
```

### 登出

```bash
coretool-cli auth logout
```

### 认证相关命令速查

| 用户意图 | 命令 |
|---------|------|
| 登录 / W3登录 | `coretool-cli auth login` |
| Token登录 | `coretool-cli auth login --token -u <工号>` |
| 公共账号登录 | `coretool-cli auth login --token --service-account -u <svc> --auth-token <token> --operator <工号>` |
| 登出 / 注销 | `coretool-cli auth logout` |
| 查看登录状态 | `coretool-cli auth status` |

## 配置管理

| 用户意图 | 命令 |
|---------|------|
| 查看配置 | `coretool-cli config list` |
| 设置配置 | `coretool-cli config set <key> <value>` |
| 查看某个配置项 | `coretool-cli config get <key>` |
| 设置下载目录 | `coretool-cli config set download-dir ~/Downloads/coretool/` |

可持久化配置项：`endpoint`、`http.timeout`、`pager`、`color`、`interactive`、`download-dir`、`username`

`debug` 当前不可通过 `config set` 持久化，不应依赖该方式开启调试。

## 执行规则

1. **环境准备**：每次会话首次使用时只校验扩展包内置的 `coretool-cli/tools/coretool-cli.exe`，记录绝对路径为 `<coretool_cmd>`；后续所有业务命令均使用该路径。

3. **从自然语言提取参数**：参见各领域参考文档中的映射表。

4. **缺少必要参数时追问**：不缺可选参数时不追问，使用默认值。

5. **JSON 参数**：Windows PowerShell 下优先使用 `--factor-file`、`--scene-factor-file`、`--data-file` 等文件参数，避免内联 JSON 被原生命令行重新转义。

6. **结果格式化**：命令输出直接展示给用户，必要时用自然语言解释表格内容。所有 CoreTest 查询命令支持 `--output json` 获取 JSON 格式输出。

7. **错误处理**：
   - `not logged in` → 引导用户执行 `coretool-cli auth login`
   - `--keyword is required` → 补充缺失参数后重试
   - HTTP 错误 → 简要说明原因（如网络问题、权限不足）
   - 可执行文件不存在或校验失败 → 停止业务操作并报告实际检查的路径
