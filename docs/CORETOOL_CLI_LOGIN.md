# CoreTool CLI 本地登录指南

在使用 `coretest-spec-e2e@0.2.3` 前，请先在本机完成 CoreTool CLI 登录。Explore 的平台 TS 查询、TS 归档以及 Archive 在线文档同步都依赖有效的 CLI 认证状态。

本文以 Windows PowerShell 和扩展包内置 CLI 为例。

## 1. 定位 CLI

将 `$Root` 修改为本机扩展包实际目录：

```powershell
$Root = "D:\TestAgent\templates\coretest-spec-e2e@0.2.3\coretest-spec-e2e"
$CoreTool = Join-Path $Root ".testagent\skills\coretool\tools\coretool-cli.exe"

Test-Path -LiteralPath $CoreTool
& $CoreTool version
```

预期结果：

- `Test-Path` 返回 `True`；
- `version` 正常输出 CLI 版本。

如果文件不存在，请确认扩展包已完整解压，并检查实际安装目录和版本号。

## 2. 使用 W3 账号登录

执行交互式登录：

```powershell
& $CoreTool auth login
```

根据 CLI 提示完成 W3 认证。登录过程中如打开浏览器，请在浏览器中完成授权，然后返回 PowerShell 等待命令结束。

不要把账号密码或 Token 写入项目文件、命令脚本、聊天记录或提交到代码仓。

## 3. 验证登录状态

登录完成后执行：

```powershell
& $CoreTool auth status
```

确认输出显示已登录，并且当前用户是准备执行测试设计和归档操作的本人账号。只有状态验证通过后，才能开始：

```text
/coretest-init
/coretest-explore
/coretest-design
/coretest-archive
```

## 4. 退出或切换账号

退出当前账号：

```powershell
& $CoreTool auth logout
```

切换账号时，先退出，再重新登录并验证：

```powershell
& $CoreTool auth logout
& $CoreTool auth login
& $CoreTool auth status
```

## 5. Token 登录（可选）

仅在明确使用 Token 的场景下执行交互式 Token 登录：

```powershell
& $CoreTool auth login --token -u <工号>
```

CLI 会提示输入 Token，Token 不会直接出现在命令行历史中。Token 登录不支持自动刷新，过期后需要重新登录。

不建议在个人终端中使用 `--auth-token <token>` 或 `-p <密码>` 的非交互式形式，以免敏感信息进入命令历史。

## 6. 常见问题

### 提示未登录

错误示例：

```text
not logged in. Run 'coretool auth login' to authenticate
```

重新执行：

```powershell
& $CoreTool auth login
& $CoreTool auth status
```

### 登录已过期或账号不正确

先退出，再重新登录：

```powershell
& $CoreTool auth logout
& $CoreTool auth login
& $CoreTool auth status
```

### CLI 文件存在，但无法执行

先单独检查：

```powershell
& $CoreTool version
```

如果仍失败，请检查文件是否完整、当前用户是否具有执行权限，以及安全软件是否拦截该可执行文件。

### 登录成功，但业务命令无权限

CLI 登录成功只代表认证有效。还需确认当前账号有权访问对应产品版本、测试设计任务、TR、IDP 文档和 Portal；权限不足时请联系相应平台管理员。

## 使用前最终检查

每次正式使用扩展包前，至少执行一次：

```powershell
& $CoreTool version
& $CoreTool auth status
```

两条命令均成功后再启动 CoreTest 流程。
