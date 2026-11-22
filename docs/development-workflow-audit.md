# 开发工作流独立审计

日期：2026-11-22

## 审计方式

- 独立子 Agent：`01a2010e-cd32-7561-814d-09adacbc52dc`，未继承主 Agent 的实现结论。
- 角色定义：`agents/upstream-issue-auditor.md`。
- 范围：当前开发工作流、canonical skill、复盘和 Cursor 薄适配；不扩展成无关全仓审计。
- 权限：只读，未编辑、格式化、提交、推送或外部写入。审计前后唯一差异是主 Agent 明确声明的 Cursor 适配新增。

## Findings 与处置

### P2：只读 review 被指引执行 mutation

- 原位置：`skills/upstream-issue-pr/references/verification.md` 的测试裁判检查同时适用于 review，却要求破坏 guard。
- 具体风险：审计者按清单在目标 worktree 修改生产代码，违反只读合同。
- 修复：mutation 限定为实施 Agent 的可写范围或一次性 scratch copy；只读 review 只能查看已有证据、使用非修改性负对照或记录缺口。

### P2：测试证据绑定 SHA，但未绑定工作树

- 原位置：`skills/upstream-issue-pr/references/verification.md` 的 PR 状态块只有 `Head`。
- 具体风险：包含未提交修改的测试结果被写成 clean commit 的验证证据。
- 修复：状态块增加 `Tree`，区分 clean head 与 `HEAD + uncommitted diff`；新 diff 也需要新的状态块。

### P3：公开写入缺少结果未知时的读回去重

- 原位置：复盘已有权限/读回教训，但 canonical workflow 只覆盖 push head。
- 具体风险：PR/comment 创建在服务端成功后客户端超时，恢复时重复 POST 或错误报告未发布。
- 修复：创建或更新后读回 ID、作者、URL 和 head；未知结果先查询，确认不存在后才重试。

三项均已修正，没有遗留未处置 finding。

## 验证

- 独立审计核对 GitHub PR、review-root 数量和 diff 数据，与复盘一致。
- 相对链接、UTF-8、文件末尾换行和尾随空白检查通过。
- `tests/test_adapters.py`：3 passed。
- `skills/upstream-issue-pr`：`quick_validate.py` 通过。
- 常见凭证模式扫描：未发现候选改动中的密钥；无符号链接。

## Cursor 原生适配

- 官方文档确认 `.cursor/agents/*.md`、独立 context、`readonly: true` 和 `/name` 调用方式：[Cursor Subagents](https://cursor.com/docs/subagents)。
- `.cursor/agents/upstream-issue-auditor.md` 的 YAML frontmatter 和 canonical 引用已验证，`readonly: true`、`model: inherit`。
- 本机 `cursor-agent` 实际只读探针返回 `Authentication required`。没有重试、重新登录或换账号，因此不声称 Cursor 原生运行已通过。

## 残余风险

- 未在 Cursor UI、OpenCode 或 Claude Code 中分别启动运行时验证；目前证明的是配置可移植和官方支持，不是所有宿主已实测。
- 未重新审计 Archon 实现代码、live E2E 或 CI。
- transcript 中的历史行为作为本地 session 证据保留，没有逐条重放。
