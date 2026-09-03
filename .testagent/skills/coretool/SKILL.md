---
name: coretool-cli
description: CoreTool CLI — 华为 CoreTool 平台开发者工具。当用户提到 CoreTool、CoreALM、需求查询、文档下载、W3 登录、coretool-cli、coretool 命令、CoreTest、InFactory、Script、Pipeline、TestResult、LCM、TestDesign、测试执行、测试结果、环境修复、测试设计、正交组合、资产库、场景、特性、功能、测试因子、模型、设计原则时使用此 skill。支持自然语言调用安装、认证、需求搜索、文档下载、测试平台操作等。
---

# CoreTool CLI Skill

CoreTool CLI 是云核IT装备部出品的统一命令行工具，支持 W3 认证、需求查询、文档下载、测试平台操作等功能。

所有命令统一使用 `coretool-cli` 调用。

## References 路由表

根据用户意图读取对应领域参考文档：
- CoreALM平台操作（需求查询 / 文档下载） → [references/corealm.md](references/corealm.md)
- 测试平台操作（InFactory、Script、Pipeline、TestResult、LCM、TestDesign） → [references/coretest.md](references/coretest.md)

## 环境准备（自动）

每次会话首次使用时，按以下步骤确保 `coretool-cli` 可用：

### 1. 检查是否已安装

```bash
which coretool-cli 2>/dev/null || which coretool-cli.exe 2>/dev/null
```

如果找到，跳到步骤3。

### 2. 安装（市场安装）

通过 AI Market 市场一键安装，自动下载二进制并配置 PATH：

```bash
# 第一步：配置 npm 仓库源（仅首次需要）
npm config set @aimarket:registry=https://cmc.centralrepo.rnd.huawei.com/artifactory/api/npm/product_npm/ strict-ssl=false

# 第二步：安装 coretool
npx @aimarket/agentcenter cli add coretool-cli@1.0.0
```

可选参数 `-g`：在命令末尾添加该参数可全局安装，不传则安装到当前项目。

安装过程中会自动打开浏览器进行 SSO 授权，授权成功后自动下载并解压二进制文件到：

- **安装目录**：`C:\Users\<用户名>\.agentcenter\bin\coretool-cli.exe`（Windows）
- **安装目录**：`~/.agentcenter/bin/coretool-cli`（Linux/macOS）

安装程序会自动将 `~/.agentcenter/bin` 添加到 Windows 用户 PATH（通过 setx），**需要重新打开终端窗口才生效**。

安装完成后，在当前 bash 会话中手动刷新 PATH：

```bash
export PATH="$HOME/.agentcenter/bin:$PATH"
```

验证安装：

```bash
coretool-cli version
```

如果市场安装失败（网络不通或 npm 不可用），提示用户检查网络或联系管理员。

### 3. 确保 PATH 生效

每次会话首次执行前，确保 PATH 包含安装目录：

```bash
# Windows (Git Bash)
export PATH="$HOME/.agentcenter/bin:$PATH"

# Linux/macOS
export PATH="$HOME/.agentcenter/bin:$PATH"
```

后续所有命令直接使用 `coretool-cli`，不再使用完整路径。

### 卸载

```bash
rm -f ~/.agentcenter/bin/coretool-cli.exe
rm -rf "$APPDATA/coretool-cli/"
```

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

当其他 CLI 工具以公共账号调用 coretool-cli 时，用 `--service-account` 标记，并用 `--operator` 指定实际操作者工号：

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

可配置项：`endpoint`、`http.timeout`、`pager`、`color`、`interactive`、`debug`、`download-dir`、`username`

## 执行规则

1. **环境准备**：每次会话首次使用时，执行 `export PATH="$HOME/.agentcenter/bin:$PATH"`，然后检查 `coretool` 是否可用，不可用则通过市场安装（`npx @aimarket/agentcenter cli add coretool-cli@1.0.0`），安装程序会自动配置 Windows 用户 PATH。

3. **从自然语言提取参数**：参见各领域参考文档中的映射表。

4. **缺少必要参数时追问**：不缺可选参数时不追问，使用默认值。

5. **结果格式化**：命令输出直接展示给用户，必要时用自然语言解释表格内容。所有 CoreTest 查询命令支持 `--output json` 获取 JSON 格式输出。

6. **错误处理**：
   - `not logged in` → 引导用户登录
   - `--keyword is required` → 补充缺失参数后重试
   - HTTP 错误 → 简要说明原因（如网络问题、权限不足）
   - 可执行文件不存在 → 通过市场安装（`npx @aimarket/agentcenter cli add coretool-cli@1.0.0`），安装程序会自动配置 PATH
