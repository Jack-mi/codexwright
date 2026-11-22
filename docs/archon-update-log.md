# Archon 更新日志

记录 build-mas 参与 Archon 上游工作时遇到的状态变化、官方反馈和后续约束。新条目置顶；事实与后续行动分开记录，不把提交、关闭、合并和验收混为一谈。

完整交互复盘见 [Archon 三个 Issue 的开发与迭代复盘](archon-pr-retrospective.md)。跨 Codex、Cursor、OpenCode 等 coding agent 的复用规则见 `skills/upstream-issue-pr/`，项目级发现入口见 `AGENTS.md`。独立子 Agent 审计及修正记录见 [开发工作流独立审计](development-workflow-audit.md)。

## 2026-11-22：#5899 关闭，不可信文本准入方案缩围

**关联链接**

- Issue：[coleam00/Archon#5765](https://github.com/coleam00/Archon/issues/5765)
- PR：[coleam00/Archon#5899](https://github.com/coleam00/Archon/pull/5899)，最终 head `379aeec1e`，已关闭但未合并
- 官方结论：[维护者关闭说明](https://github.com/coleam00/Archon/pull/5899#issuecomment-7068134089)

**我们尝试的实现**

- 目标是让不可信作者的文本在可信人员接受其精确版本之前不能进入 Agent，并把接受决定绑定到标题和正文摘要；文本编辑后，原接受决定失效。
- 为覆盖运行期间的“不可信文本不接触 Agent”边界，实现涉及 Provider 和工具能力限制。

**碰到的问题**

- 完整限制需要拒绝 shell、Web、MCP、插件、技能和脚本工具。当时只有 Claude 能执行这套限制，与 Archon 的 Provider 中立原则冲突；Agent 不能使用 shell 时也无法正常构建，保证的实际用途大体只剩 triage。
- 官方当前真正需要的保证更小：外部作者的文本未经可信人员接受其精确版本时，不得启动 run。一次 Forge 信任读取和一次启动前检查即可满足，不需要限制 run 启动后的 Provider 或工具能力。

**官方结论与当前状态**

- 维护者明确说明，关闭原因是原 issue 要求的目标形态，而不是实现质量；原 issue 要求过多，责任在官方需求制定。
- `#5765` 已改写为“运行开始前校验可信来源和文本摘要”，保持开放；`#5899` 未合并，不代表方案已经上线。
- 新范围暂缓到软件工厂建设来自公共 tracker 的常驻 intake 时再实施，不是当前需要继续推进的任务。

**后续复用约束**

- 可以复用本次的 `workitem.trust` 读取，以及标题和正文的 digest 绑定。
- 后续实现应采用一次 Forge 读取（作者、编辑者、文本 digest、已接受 digest）和一次 run preparation 检查；文本编辑后必须重新接受。
- 不沿用限制 Provider、工具或节点类型的 protected mode，不重开原来的大范围 PR，也不在常驻 intake 启动前提前扩建该能力。
