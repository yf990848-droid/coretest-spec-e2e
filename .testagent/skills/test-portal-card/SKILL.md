---
name: test-portal-card
description: 统一的卡片消息通信技能，负责向 webapps/default/index.html 发送卡片消息。支持 working（占位）和 completed（带数据）两种状态，所有阶段的消息统一通过此 skill 发送。userId 通过 getpass.getuser() 自动获取，无需传递。
metadata:
  author: testAgent
  version: "1.0.1"
---

# 卡片消息通信

统一的卡片消息通信技能，所有消息都发送给 `webapps/default/index.html` 前端页面。userId 通过 `getpass.getuser()` 自动获取，无需外部传递。

## 核心职责

- 创建 working 状态卡片（流程开始时占位）
- 创建 completed 状态卡片（流程完成时带数据覆盖）
- userId 自动获取，不需要传参
- 前端页面通过 postMessage 接收卡片 data 中的数据

## 执行步骤

### 方式1: 初始化 working 卡片

流程开始时，创建 working 状态卡片并携带默认版本参数，让 iframe 立即加载 FullTestDesign Portal：
```bash
cd .testagent/skills/test-portal-card/scripts;
python -u card_generate.py "working" "coretest-explore"
```
参数说明：
- 第1个参数: 状态，固定值 `working`
- 第2个参数: cardName，FullTestDesign 全链路固定为 `coretest-explore`

working 状态默认使用内置版本参数（versionPbi=7414819），userId 自动通过 getpass 获取。也可额外指定参数：
```bash
python -u card_generate.py "working" "coretest-explore" "{versionPbi}" "{analyseId}" "{pageType}" "{userId}"
```
- 第3个参数: versionPbi，版本PBI编号（可选，默认7414819）
- 第4个参数: analyseId，TR/TS/TP路由中的ID（可选）
- 第5个参数: pageType，可选值: `fullTestDesign`(默认), `TR`, `TS`, `TP`
- 第6个参数: userId（可选，不传则通过 getpass.getuser() 自动获取）

### 方式2: 发送 completed 卡片（带数据）

流程完成时，发送 completed 状态卡片覆盖 working 卡片：
```bash
cd .testagent/skills/test-portal-card/scripts;
python -u card_generate.py "completed" "coretest-explore" "{versionPbi}" "{analyseId}" "{pageType}" "{userId}"
```
参数说明：
- 第1个参数: 状态，固定值 `completed`
- 第2个参数: cardName，固定为 `coretest-explore`，与 working 阶段保持一致，用于覆盖同一卡片
- 第3个参数: versionPbi，版本PBI编号
- 第4个参数: analyseId，TR/TS/TP路由中的ID
- 第5个参数: pageType，可选值: `fullTestDesign`(默认), `TR`, `TS`, `TP`
- 第6个参数: userId（可选，不传则通过 getpass.getuser() 自动获取）

**重要**：必须先cd到脚本的目录，然后使用python -u card_generate.py执行，不要直接使用绝对路径调用python脚本，命令间隔使用;号，不得使用&&符号

## 成功准则

1. 脚本执行成功，输出 success: True
2. working 状态卡片返回 card_cache_id 并保存 card_id
3. completed 状态卡片复用同一 card_id 覆盖 working 卡片

## 通信协议

卡片与前端页面遵循 TestAgent Iframe 通信协议（参考 Wiki: WIKI2026042310875841）：

### 前端接收（InCardDataType）
TestAgent 平台通过 postMessage 将卡片 data 发送给 iframe：
```json
{
  "type": "chat",
  "data": { "versionPbi": "...", "userId": "...", "analyseId": "...", "pageType": "fullTestDesign" },
  "status": "completed",
  "cardId": "xxx"
}
```
pageType 可选值: `fullTestDesign`, `TR`, `TS`, `TP`，对应前端路由：
- `fullTestDesign` → `#/fullTestDesign?versionPbi=...&userId=...`
- `TR` → `#/fullTestDesign/trAnalyse6_{analyseId}?versionPbi=...&userId=...`
- `TS` → `#/fullTestDesign/tsAnalyse14_{analyseId}?versionPbi=...&userId=...`
- `TP` → `#/fullTestDesign/tpAnalyse19_{analyseId}?versionPbi=...&userId=...`

### 前端发送（OutCardDataType）
前端页面加载完成后发送 iframeReady：
```json
{
  "type": "iframeReady",
  "data": null,
  "prompt": "",
  "action": "ready"
}
```

## cardName

FullTestDesign 的 init、explore、design、archive 阶段必须统一使用 `coretest-explore`，复用同一个 `coretest-explore_card_id.txt`。不得因当前阶段改用 `coretest-design` 或 `coretest-archive`，否则会生成新的 card_id，无法覆盖原卡片。

## 技术说明

- 使用方式2（card/cache 接口）发送，避免数据占用模型上下文
- card_id 持久化在 scripts/ 目录下，working 和 completed 共用同一 card_id 实现覆盖
- userId 支持脚本传参，不传则通过 `getpass.getuser()` 自动获取
