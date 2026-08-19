# CoreALM 领域参考

CoreALM 是华为 CoreTool 平台的需求管理领域，支持需求查询、需求详情、需求关系、文档下载等功能。

所有命令通过 Bash 工具执行。

### 认证相关

#### 登录 / 认证 / W3登录 / 登录CoreTool

```bash
coretool-cli auth login
```

交互式登录，按提示输入工号和密码。

#### Token登录 / 用token登录

```bash
coretool-cli auth login --token -u <工号>
# 示例
coretool-cli auth login --token -u 30022769
```

#### 公共账号登录 / 服务账号登录

```bash
coretool-cli auth login --token --service-account -u <公共账号> --auth-token <token> --operator <操作者工号>
# 示例
coretool-cli auth login --token --service-account -u svc001 --auth-token eyJhbGci... --operator 30022769
```

#### 登出 / 注销 / 退出登录

```bash
coretool-cli auth logout
```

#### 查看登录状态 / 我登录了吗 / 当前用户

```bash
coretool-cli auth status
```

### 需求查询

包含需求搜索、需求详情、需求关系、个人需求（开发需求 + 个人IR/SR需求）。

#### 搜索需求 / 查需求 / 找需求

```bash
coretool-cli corealm requirement list --keyword <关键词>
# 示例：搜一下5G相关的需求
coretool-cli corealm requirement list --keyword 5G
```

可选筛选：`--type IR|SR`、`--page 2 --page-size 20`、`--version-id <版本ID>`、`--belong-version-id <归属版本ID>`

#### 查看需求详情 / 需求描述

```bash
coretool-cli corealm requirement view <e2e-id>
# 示例：看看IR20260803000961的详情
coretool-cli corealm requirement view IR20260803000961
```

#### 查IR下的SR / IR子需求

```bash
coretool-cli corealm requirement ir-children <ir-e2e-id>
# 示例
coretool-cli corealm requirement ir-children IR20260803000961
```

#### 查SR的父IR / SR属于哪个IR

```bash
coretool-cli corealm requirement parent-ir <sr-e2e-id>
# 示例
coretool-cli corealm requirement parent-ir SR20260803001234
```

#### 查我的开发需求 / 我的Story / 我的US

```bash
coretool-cli corealm requirement dev-requirements
# 查所有（含已关闭）
coretool-cli corealm requirement dev-requirements --all
# 查某人的
coretool-cli corealm requirement dev-requirements --assignee "weiwei 30022769"
# 分页
coretool-cli corealm requirement dev-requirements --page 2 --page-size 20
```

#### 查我的IR / 我负责的IR / 我的个人需求

```bash
coretool-cli corealm requirement my-requirements
# 查我的SR
coretool-cli corealm requirement my-requirements --type SR
# 查所有（含已关闭）
coretool-cli corealm requirement my-requirements --all
# 查某人的IR
coretool-cli corealm requirement my-requirements --assignee "weiwei 30022769"
# 查某人的SR
coretool-cli corealm requirement my-requirements --type SR --assignee "weiwei 30022769"
```

**说明**：
- `dev-requirements` 查询 Story/US 类型的开发需求，`my-requirements` 查询 IR/SR 类型的个人需求
- `my-requirements` 默认查询 IR 类型，加 `--type SR` 查询 SR
- 两个命令默认只显示未关闭的需求，加 `--all` 显示全量
- `--assignee` 接受长工号（如 `weiwei 30022769`），默认使用当前登录用户的长工号
- 当用户明确说"开发需求"或需求类型为 US/Story/UserStory 时，应使用 `dev-requirements`
- 当用户说"我的IR"、"我负责的需求"、"个人需求"时，应使用 `my-requirements`

### 文档操作

#### 查需求文档列表

```bash
coretool-cli corealm document list --requirement <e2e-id>
# 示例
coretool-cli corealm document list --requirement IR20260803000961
```

#### 下载需求的所有文档

```bash
coretool-cli corealm document list --requirement <e2e-id> --download
# 示例：下载IR20260803000961的文档
coretool-cli corealm document list --requirement IR20260803000961 --download
# 示例：下载多个需求的文档
coretool-cli corealm document list --requirement IR20260803000961,IR20260803000962 --download
# 示例：只下载IDP类型
coretool-cli corealm document list --requirement IR20260803000961 --download --type idp
# 示例：包含群组文档
coretool-cli corealm document list --requirement IR20260803000961 --download --include-group-docs
```

#### 下载单个文档

```bash
coretool-cli corealm document download <doc-id> --type <idp|dbox>
# 示例：下载IDP文档
coretool-cli corealm document download DOC20260803001 --type idp
# 示例：下载DBOX文档
coretool-cli corealm document download DOC20260803001 --type dbox
# 示例：指定下载目录
coretool-cli corealm document download DOC20260803001 --type idp --output-dir ~/Desktop/
```

**重要**：下载需求文档时，优先使用 `document list --requirement <e2e-id> --download`，它会自动在下载目录下创建以需求ID命名的子目录（如 `~/Downloads/coretool/corealm/IR20250821000344/`）。仅下载单个文档时才用 `document download <doc-id>`。支持同时指定多个需求ID，逗号分隔或重复 `--requirement` 均可。

### 缺少必要参数时追问

- 搜索需求缺关键词 → 问用户搜什么
- 查看详情/下载文档缺 ID → 问用户具体 ID
