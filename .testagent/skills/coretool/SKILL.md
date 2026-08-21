---
name: coretool-cli
description: CoreTool CLI — 华为 CoreTool 平台开发者工具。当用户提到 CoreTool、CoreALM、需求查询、文档下载、W3 登录、coretool-cli、coretool 命令、CoreTest、InFactory、Script、Pipeline、TestResult、LCM、TestDesign、测试执行、测试结果、环境修复、测试设计、正交组合、资产库、场景、特性、功能、测试因子、模型、设计原则时使用此 skill。支持自然语言调用安装、认证、需求搜索、文档下载、测试平台操作等。
---

# CoreTool CLI Skill

CoreTool CLI 是华为 CoreTool 平台的命令行工具，支持 W3 认证、需求查询、文档下载、测试平台操作等功能。

每次会话首次使用时先解析 CoreTool CLI 的绝对路径并记为 `<coretool_cmd>`。后续命令中的 `coretool` 仅表示命令名占位符，实际执行时必须替换为带引号的 `<coretool_cmd>`。

## References 路由表

根据用户意图读取对应领域参考文档：
- 需求查询 / 文档下载 → [references/corealm.md](references/corealm.md)
- 测试平台操作（InFactory、Script、Pipeline、TestResult、LCM、TestDesign） → [references/coretest.md](references/coretest.md)

## 环境准备（自动）

每次会话首次使用时，按以下顺序解析可用 CLI，并记录最终的绝对路径为 `<coretool_cmd>`。不要依赖某次 shell 中修改的 PATH 或环境变量能在后续工具调用中继续生效。

### 1. 优先使用扩展包内置 CLI

`<extension-root>` 表示包含当前 `.testagent` 目录的扩展根目录。按固定顺序检查：

1. `<extension-root>/.testagent/skills/coretool/tools/coretool-cli.exe`
2. `<extension-root>/.testagent/skills/coretool/tools/coretool.exe`
3. `<extension-root>/.testagent/skills/coretool/tools/coretool-cli`
4. `<extension-root>/.testagent/skills/coretool/tools/coretool`

可在同一 shell 中按下面的逻辑解析；`<extension-root>` 必须替换为已确定的绝对路径：

```bash
CORETOOL_CMD=""
TOOL_DIR="<extension-root>/.testagent/skills/coretool/tools"

for candidate in \
  "$TOOL_DIR/coretool-cli.exe" \
  "$TOOL_DIR/coretool.exe" \
  "$TOOL_DIR/coretool-cli" \
  "$TOOL_DIR/coretool"; do
  if [ -f "$candidate" ] && "$candidate" version >/dev/null 2>&1; then
    CORETOOL_CMD="$candidate"
    break
  fi
done
```

候选文件存在但 `version` 校验失败时，不中断解析，继续检查 PATH。

### 2. 回退到系统 PATH

扩展包内没有可用 CLI 时，按以下顺序从 PATH 查找并执行 `version` 校验：

```bash
for command_name in coretool coretool.exe coretool-cli coretool-cli.exe; do
  candidate="$(command -v "$command_name" 2>/dev/null || true)"
  if [ -n "$candidate" ] && "$candidate" version >/dev/null 2>&1; then
    CORETOOL_CMD="$candidate"
    break
  fi
done
```

### 3. 仍未找到时自动安装

保留 AI Market 自动安装兜底：

```bash
# 第一步：配置 npm 仓库源（仅首次需要）
npm config set @aimarket:registry=https://cmc.centralrepo.rnd.huawei.com/artifactory/api/npm/product_npm/ strict-ssl=false

# 第二步：安装 coretool
npx @aimarket/agentcenter cli add coretool-cli@0.0.6
```

可选参数 `-g`：在命令末尾添加该参数可全局安装，不传则安装到当前项目。

安装过程中会自动打开浏览器进行 SSO 授权，授权成功后自动下载并解压二进制文件到：

- **安装目录**：`C:\Users\<用户名>\.agentcenter\bin\coretool-cli.exe`（Windows）
- **安装目录**：`~/.agentcenter/bin/coretool-cli`（Linux/macOS）

安装完成后，不要求重开终端；直接依次检查以下已知路径和 PATH，并再次执行 `version` 校验：

1. `$HOME/.agentcenter/bin/coretool-cli.exe`
2. `$HOME/.agentcenter/bin/coretool-cli`
3. 步骤 2 中的 PATH 候选

如果市场安装失败，或安装后仍没有候选通过校验，停止业务操作并提示用户检查网络、安装权限或联系管理员。

### 4. 后续命令调用

将最终通过校验的绝对路径记录为 `<coretool_cmd>`。同一 shell 中可执行 `"$CORETOOL_CMD" ...`；跨 shell 或跨工具调用时，直接使用已记录并加引号的绝对路径。

本文及 references 中形如：

```bash
coretool auth status
```

的命令，实际执行为：

```bash
"<coretool_cmd>" auth status
```

### 卸载

```bash
rm -f ~/.agentcenter/bin/coretool-cli.exe
rm -rf "$APPDATA/coretool-cli/"
```

## 认证

所有业务命令执行前需先登录。未登录时会提示 `not logged in. Run 'coretool auth login' to authenticate`。

### W3 登录（个人账号，推荐）

交互式：
```bash
coretool auth login
```

非交互式：
```bash
coretool auth login -u <工号> -p <密码>
```

### Token 登录

交互式（安全，token 不进 shell history）：
```bash
coretool auth login --token -u <工号>
```

非交互式（CI/脚本场景）：
```bash
coretool auth login --token -u <工号> --auth-token <token>
```

注意：Token 登录不支持自动刷新，过期后需重新登录。

### 公共账号登录（服务账号 + 操作者）

当其他 CLI 工具以公共账号调用 coretool 时，用 `--service-account` 标记，并用 `--operator` 指定实际操作者工号：

```bash
coretool auth login --token --service-account -u <公共账号> --auth-token <token> --operator <操作者工号>
```

- 公共账号模式下，业务命令使用操作者身份（工号、姓名、邮箱），而非公共账号身份
- 操作者身份也可通过环境变量 `CORETOOL_OPERATOR` 指定

### 查看登录状态

```bash
coretool auth status
```

### 登出

```bash
coretool auth logout
```

### 认证相关命令速查

| 用户意图 | 命令 |
|---------|------|
| 登录 / W3登录 | `coretool auth login` |
| Token登录 | `coretool auth login --token -u <工号>` |
| 公共账号登录 | `coretool auth login --token --service-account -u <svc> --auth-token <token> --operator <工号>` |
| 登出 / 注销 | `coretool auth logout` |
| 查看登录状态 | `coretool auth status` |

## 配置管理

| 用户意图 | 命令 |
|---------|------|
| 查看配置 | `coretool config list` |
| 设置配置 | `coretool config set <key> <value>` |
| 查看某个配置项 | `coretool config get <key>` |
| 设置下载目录 | `coretool config set download-dir ~/Downloads/coretool/` |

可配置项：`endpoint`、`http.timeout`、`pager`、`color`、`interactive`、`debug`、`download-dir`、`username`

## 执行规则

1. **环境准备**：每次会话首次使用时，严格按“扩展包内置 CLI → 系统 PATH → AI Market 自动安装”的顺序解析并校验 CLI，记录绝对路径为 `<coretool_cmd>`；后续所有业务命令均使用该绝对路径。

3. **从自然语言提取参数**：参见各领域参考文档中的映射表。

4. **缺少必要参数时追问**：不缺可选参数时不追问，使用默认值。

5. **结果格式化**：命令输出直接展示给用户，必要时用自然语言解释表格内容。所有 CoreTest 查询命令支持 `--output json` 获取 JSON 格式输出。

6. **错误处理**：
   - `not logged in` → 引导用户登录
   - `--keyword is required` → 补充缺失参数后重试
   - HTTP 错误 → 简要说明原因（如网络问题、权限不足）
   - 可执行文件不存在或校验失败 → 继续下一层解析；扩展包和 PATH 均不可用时通过市场安装，安装后仍不可用则停止并提示用户
