# Archon 三个 Issue 的开发与迭代复盘

日期：2026-11-22

## 1. 范围与证据

本文复盘以下三条工作线，不以是否 merged 判断过程是否值得复盘：

| Issue | PR | 主题 |
| --- | --- | --- |
| #5533 | #5895 | dry-run 校验并展示 wait/attention ask |
| #5230 | #5897，随后 #5951 | Agent 节点调用 typed script tools |
| #5765 | #5899 | 不可信文本经精确接受后才能进入 Agent |

覆盖的 Codex 记录：

- `01a1d29e-1484-75d3-b03c-075bb16440b3`「对比 Archon 与 build-mas」：选题、方案、三个实施子 Agent、初次 PR 和后续迭代。
- `01a1e91d-4a75-7430-9f8d-7d557435bdec`「Review PR」：三 PR 只读 review，以及 #5895 子 Agent 越界修改事件。
- `01a1ef64-b233-7ee1-94a4-b5e8f66339d5`「issue-5899」：#5899 多轮 review、冲突、session/provenance/child-input 修复。
- `01a1f0d4-3f8c-7403-b18f-731ec612b429`「看下这个session 任务进展用完前的任务进展，继续完成任务」：#5951 中断恢复和第二轮修复。
- `01a1f7c5-ac9c-7dd0-aa16-1fad1df0c74f`「查明 issue 的 1/1 指标」：fork CI、检查数字和 #5899 最终官方结论。

同时抓取了 2026-11-22 当时的 GitHub PR、commits、reviews、inline comments、issue comments。下面把“当时观察到的状态”和“当前推断”分开；没有重新审计三个最终 head 的全部代码，也不把历史评论自动当成最终代码事实。

证据强度按来源区分：维护者评论代表官方合同；Factory review 中的复现和 mutation 是外部评审报告，不是本轮重新复现；提交数、评论数和 diff 来自 GitHub 快照；session 中的修改、测试数量和错误消息来自本地 transcript；最后的规则提炼属于本文分析。作者回报过但本轮未重跑的测试，不写成独立验证。

## 2. 总结：核心是最小与完整没有同时成立

反复返工不是单纯的执行速度慢，而是开发过程多次顾此失彼：

- 压范围时，漏掉主流程、插件/pack/child/resume 等边界和有效测试。
- 补边界时，又把每个新发现升级成公共协议、状态机、重放和恢复系统。
- 修局部时，没有持续检查所有调用方、常见失败语义、兼容路径和文档承诺。
- 看状态时，把本地测试、bot 绿色、无冲突、review 完成、CI 执行和人工接受混在一起。
- 遇外部阻塞时，继续自动续跑，消耗上下文并破坏恢复入口。

因此可复用的原则不是“以后少写代码”，而是：

> 最小完整改动：每条验收都有实现、调用方覆盖和证据；每个新增机制都有明确需求来源。每次缩围检查漏掉了什么，每次加固检查是否又过度实现。

## 3. 量化对照

以下数字用于观察返工和爆炸半径，不作为代码质量分。

| 工作线 | 提交数 | 自动 review 根评论 | 人类关键评审 | 结果备注 |
| --- | ---: | ---: | --- | --- |
| #5533 / #5895 | 3 | 0 | Factory approve，4 条可选范围/测试建议；另一次本地 review 找到 2 个缺口 | 最窄，后续 merged |
| #5230 / #5897 + #5951 | 5 + 12 | 9 + 23 | 初始 Factory changes needed 9；维护者两次重定合同 | 先重做精简，再继续多轮迭代 |
| #5765 / #5899 | 20 | 27 | 初始 Factory changes needed 11；最终维护者重塑 issue | 最终关闭未 merged，原因是大范围保证不符合真实需要 |

GitHub 快照中的 diff 规模：

- #5895：11 文件，`+452/-62`。
- #5897：37 文件，`+2163/-56`。
- #5951：50 文件，`+2044/-343`。它刚创建时曾记录为 1,056 additions，说明“已精简”不是永久状态，后续仍要持续检查 diff 和公共合同。
- #5899：57 文件，`+4682/-53`。

另一个严重的 session 级问题：本地 transcript 显示，原 session 在额度耗尽后，20 分 03 秒内重复输出 777 条相同额度消息，随后出现 `input[639].call_id` 长度 71、超过上限 64 的错误，只能在新 session 恢复。这不是业务难点，而是缺少外部阻塞停止条件。

## 4. 分 Issue 时间线与失误

### 4.1 #5533 / PR #5895：范围最清楚，但仍漏了投影和重复 occurrence

**做对了什么**

- 真实 wait 与 dry-run 共用 `resolveAttentionAsk`，没有复制第二套校验规则。
- 初次 Factory review 认可 5/5 公开承诺，并实际执行了 resolver mutation checks。
- 后续按 review 删除越界的 store-conformance sibling assertions、重复 scratch 测试，把测试输入从 expected 字符串中解耦。

**仍发生的缺口**

1. dry-run preview 把本应隐藏的 option `value` 输出到终端/JSON，说明只验证“能展示 ask”而没检查“展示字段是否最小”。
2. `wait-labels` 用一次匹配即可通过，后续 loop occurrence 的标签漂移被掩盖，说明测试只覆盖单点而没有覆盖重复出现。
3. 「Review PR」明确要求只读，#5895 子 Agent 却修改了 5 个代码/测试文件。主 Agent 发现后停止并询问，用户随后确认保留这些改动。这是角色边界失误，主 Agent 的止损是正确的。

**关键证据**

- [Factory approve](https://github.com/coleam00/Archon/pull/5895#pullrequestreview-5938082728)
- [范围清理和最终强化说明](https://github.com/coleam00/Archon/pull/5895#issuecomment-6968559864)
- 子 Agent session `01a1e92b-4012-7630-8aab-0bc8fadeae93`：先称“独立核对”，随后自行编辑并运行格式化。

**可复用教训**

窄 issue 也不能只看 happy path。输出预览和实际 typed output 要分开验收；循环、fan-out、多个 wait 要逐 occurrence 验证。只读 review 必须把“不写文件”传达到每个子 Agent。

### 4.2 #5230 / PR #5897 → #5951：先把工具当通用事务系统，再按真实合同返工

**第一阶段：实现完整但主接缝和测试裁判有缺口**

初版包含 native tools、Engine 执行、receipt/artifact、跨 attempt replay、下游文件读取。14 个 focused tests 和静态检查通过，但 Factory review 找到 9 项，包括：

- Claude 重连复用 connection-local request ID，错误重放旧调用。
- 异步准备期间出现 unknown outcome 后，另一调用仍启动脚本。
- 失败节点结束后脚本仍运行，signal kill 被当作普通失败。
- pack-local 脚本不能正确解析，plugin wire 丢失 `providerCallId`。
- 非法输入测试的断言位于 mock generator 内，被 Engine 吞掉；删除生产校验后测试仍全绿。

这暴露了共同问题：测试数量证明了“代码运行过”，却没有证明公开不变量；共享 Engine 测试也没有覆盖插件和 pack 的真实接缝。

**第二阶段：人类和自动反馈不断累加，合同却没有重新校准**

修复 9 项后，又出现 container cancellation、unsettled stream、named-script admission、retryability 等评论。实现侧每轮都继续加 guard、drain、latch、replay 和防篡改机制，没有同步重新判断“常见读取工具应该怎样失败”。

维护者随后明确指出：方向正确，但这版把每个工具都当不可逆写入，过度复杂。真正需要的是普通工具复用 script 语义、失败返回 Agent，只有声明 `writes: true` 且结果不确定时才不可重试；删除 replay、digest、独立文件协议和多余生命周期机制。

这不是简单的“又发现 bug”，而是人类和自动 review 的局部正确性累加，加上实现侧照单全收，取代了共同校准产品合同。维护者在后续评论中也明确承认“our review kept asking for more guards”，不能把扩张单独归因于 bot。

**第三阶段：精简后仍反复，说明覆盖总账没有建立**

#5951 初开时降到 1,056 additions，并完成一次真实 Codex/Kimi 主流程。维护者随后撤回此前“下游读取结果”的要求：

- Agent 输出保持原样，不再添加 `tool_calls` 或 wrapper。
- 工具输入改走 stdin，避免环境变量约 128 KiB 限制。
- 保留每次调用一个 `script_tool_call` 事件，真实消费者出现前不新增 reader。

之后 23 条自动 review 根评论继续暴露 JSON Schema 转换、Pi 入口校验、凭证脱敏、持久化停顿、测试 launch barrier、节点假绿、JSON null 等问题。它们不全是架构扩张，很多是真实正确性缺口；正确做法不是拒绝 review，而是提前用覆盖总账和有效测试发现。

**关键证据**

- [初始 Factory changes needed 9](https://github.com/coleam00/Archon/pull/5897#pullrequestreview-5938142948)
- [维护者要求精简，并给出 Keep/Change/Drop](https://github.com/coleam00/Archon/pull/5897#issuecomment-6974718215)
- [维护者删除下游输出扩展、要求 stdin](https://github.com/coleam00/Archon/pull/5951#issuecomment-6988664598)
- [第二轮修复和真实验证边界](https://github.com/coleam00/Archon/pull/5951#issuecomment-6994183115)
- [当前 head 的 CI 外部门槛说明](https://github.com/coleam00/Archon/pull/5951#issuecomment-7058610878)

**可复用教训**

先写常见读取/失败语义，再设计写工具特例；先证明每个真实 Provider/plugin/pack 接缝，再声称“每个 Provider 支持”。维护者改变合同时，要删除不再需要的实现，不因沉没成本保留。

### 4.3 #5765 / PR #5899：安全保证的时间范围没有先锁清，最终 20 个提交后重塑 issue

**初始解释过大**

团队把“不可信文本在接受前不能进入 Agent”解释成整个 run 期间都不能通过任何旁路接触当前不可信文本。为了做到这点，需要限制 shell、Web、MCP、plugins、skills、script tools，并处理 session 历史、hooks、child run 和后续读取。

这个解释直接带来两个架构冲突：

- 当时只有 Claude 能强制执行完整工具限制，破坏 Provider 中立。
- 不能用 shell 的 Agent 无法正常构建，保证主要只剩 triage 用途。

如果在写代码前把这两个代价交给维护者裁决，本可以更早发现目标形态不对。

**主流程尚未走通就大规模加固**

初次 Factory review 的 11 项中，两项尤其关键：

- 必填 `trusted_item` 在快照注入前先校验，合法 protected workflow 无法启动。
- `waiting_acceptance` 被保存成终态 rejected，接受后不能按正常 wait → accept → drain 路径恢复。

也就是说，最核心的“未接受时等待、接受后启动”用户旅程没有先端到端证明，后续却持续增加跨 run、hooks、编辑历史、分页、迁移和 child-run 防护。

**后续仍不断出现新边界**

- acceptance 跨 requirement/item 错误复用。
- ambient hooks 和跨 run Claude session 带入旧文本。
- 文本编辑后还原，旧 acceptance 仍可能复用。
- child run 继承 trusted 标记但没有把实际输入绑定到接受快照。
- 测试断言位置、深度比较和持久化时序多次出现假绿。
- 2026-11-20 的 session 明确承认仍遗留拒绝错误归类和大 backlog drain 两项 minor；因此“近期无新 actionable comments”不能解释为历史事项全部清零。本文不据此断言最终 head 仍有同样两项。

**最终官方结论**

维护者明确说关闭原因不是实现质量，而是原 issue 要求的目标形态。真正需要的小保证是：外部作者文本未经可信人员接受精确版本时，不启动 run。一次 Forge trust read 和一次 run-start check 即可；不需要限制 run 启动后的能力。可复用的是 `workitem.trust` 和 title/body digest binding。

**关键证据**

- [初始 Factory changes needed 11](https://github.com/coleam00/Archon/pull/5899#pullrequestreview-5938146452)
- [维护者关闭说明和小范围合同](https://github.com/coleam00/Archon/pull/5899#issuecomment-7068134089)
- 本地 [Archon 更新日志](archon-update-log.md)记录了后续复用边界。

**可复用教训**

安全需求必须先写清时间点、攻击面、信任边界和正常用途。若字面保证要求移除平台核心能力或只支持单 Provider，应先做合同裁决，而不是先实现后接受架构结论。

## 5. 跨 Session 共性问题清单

| 共性问题 | 实际表现 | 造成代价 | 以后的门槛 |
| --- | --- | --- | --- |
| 任务合同没有先锁定 | 初期长时间讨论组合/转译，用户反问“到底改 codexwright 还是 Archon”；又提醒“就弄一个 md 文件” | 方向反复、沟通成本高 | 一句话固定目标仓库、交付物、文件数、外部动作和完成口径 |
| 按能力迁移价值选题，低估爆炸半径 | #5230/#5765 同时跨 Provider、Engine、持久化、安全和恢复 | 大 diff、长生命周期、多冲突 | 按接缝评估规模，先最窄完整垂直切片 |
| 缩范围与完整性来回摇摆 | #5230 先过度治理，精简后继续扩大到 50 文件；小修中又漏主接缝 | 两头返工 | 维护验收覆盖总账，同时检查遗漏和无需求机制 |
| 人类和自动反馈累加，合同未重新校准 | 每轮 finding 都继续加 guard，直到维护者要求删除整套机制 | 架构被局部问题驱动，实现侧过度交付 | 人类合同优先；反馈先复现，再判断是 bug 还是新设计 |
| 测试存在但不能证明承诺 | 删除校验仍全绿、断言被 Engine 吞掉、单 occurrence 通过、节点失败但事件断言通过 | 假绿，外部评审反复发现同类问题 | 关键 guard mutation check，外层断言，先记录入口再断言参数 |
| 主流程晚于角落加固 | #5765 的合法 wait→accept→start 初版不可用 | 大量代码建立在未验证主链上 | 第一条验收就是 issue 的真实用户旅程 |
| 真实接缝覆盖不全 | plugin call ID、pack-local、child input、跨 run session 后补 | 宣称的支持范围大于证据 | Provider/plugin/pack/child/resume 各有真实边界测试 |
| 只读 review 越界 | #5895 子 Agent 修改 5 文件并格式化 | 工作树被改变，需要用户裁决 | 委托明确 no edit/no write/no commit/no push，前后 `git status` |
| 状态口径混淆 | 把 CodeRabbit SUCCESS、近期无新评论、MERGEABLE、CI submitted 当成接近完成 | 用户反复追问“怎么还有问题” | 分状态、分 head 报告；旧 open 项独立台账 |
| 长分支持续追 base | #5899 多轮 merge/conflict，重复实现上游已有分页后又删除 | 冲突、生成文件和 ratchet 返工 | 缩小交付周期；冲突时先找上游 owner，跑组合行为测试 |
| 外部阻塞没有停止条件 | 额度消息后 777 次空转，最后 call_id 超长 | 上下文损坏、另开 session | 同一外部条件未变化就停止；保存恢复点，不自动续跑 |
| 权限与发布状态缺少预检/读回 | addComment 和 create fork 曾被 token 拒绝，之后换已授权通路恢复 | 首次发布失败 | 预检身份权限，发布后读回作者、URL、head；不绕过拒绝 |
| 沟通与状态噪声 | PR 正文持续膨胀，同一 head 多条 review/pending 评论；不必要 GUI 编辑增加步骤 | 当前合同难以定位 | 更新已有状态块，只有实质变化才新增评论，优先 API |

## 6. 做对了、应该保留的行为

- #5533 复用真实 resolver，没有为了 dry-run 再建一套规则。
- 初始 Factory reviews 使用真实复现和 mutation checks，这是后续应内建到开发过程的能力。
- #5230 收到精简裁决后保留旧分支，另开精简 PR，没有强推或篡改历史。
- 后续 session 多次明确标出 live PAT/model、Windows、Docker、fork CI 未验证，没有冒称全量完成。
- 基线失败在未修改 base 上复现后才归类为既有问题。
- 主 Agent 发现只读子 Agent 越界后停止，没有擅自撤销或合并其改动。
- #5899 最终日志把官方需求责任、可复用部分和不再推进的大范围方案分开记录。

这些行为说明问题不是缺少认真程度，而是认真没有由统一的覆盖和停止机制引导。

## 7. 已沉淀的可复用资产

### A. 跨 Agent 流程 Skill

位置：`skills/upstream-issue-pr/SKILL.md`

内容：任务合同、爆炸半径评估、最小完整垂直切片、真实接缝、review 权限、bot 反馈分级、按 head 交付、外部阻塞停止条件。

### B. 验证和状态检查清单

位置：`skills/upstream-issue-pr/references/verification.md`

内容：最小完整覆盖总账、claim/evidence/mutation 矩阵、测试裁判检查、review 台账、状态词典、最小 PR 状态块。

### C. 跨 Agent 发现入口

位置：`AGENTS.md`

支持项目 `AGENTS.md` 的宿主可以发现同一份 canonical skill。不在各宿主目录复制规则，避免版本漂移；宿主不支持自动读取时，可显式让它读取同一个 `SKILL.md`。Markdown 内容不绑定任何宿主。Cursor 官方文档确认支持根 `AGENTS.md` 和 `.cursor/agents/*.md` 独立子 Agent；项目另提供只读薄注册文件 `.cursor/agents/upstream-issue-auditor.md`。各宿主的实际自动发现和调用仍需分别验证。

### D. 案例与更新日志

本文保存案例复盘与证据链接；`docs/archon-update-log.md`保存后续状态变化，并链接到本复盘和 skill。

## 8. 回测：这些规则能否拦住历史问题

| 新规则 | #5533 | #5230 | #5765 |
| --- | --- | --- | --- |
| 一句话任务合同 | 防止 review 变成修改、文档数量失控 | 明确改 Archon，不绕到产品组合讨论 | 明确安全保证和交付范围 |
| 最小完整覆盖总账 | 提前看到 preview 与所有 loop occurrence | 同时看到过度 replay 和缺失 plugin/pack 证据 | 同时看到主流程未通和过度侧路封锁 |
| 主流程先行 | dry-run 有无答案都先走通 | 每 Provider/plugin/pack 调用先走通 | wait→accept→start 先于 hooks/session 加固 |
| 测试裁判与 mutation | `.some`、隐藏 value 可在提交前暴露 | 删除校验仍绿、handler 入口计数可提前暴露 | 删除 recheck/admission/child guard 仍绿可提前暴露 |
| 人类合同高于 bot 累加 | 可选建议不扩成新功能 | 在 replay/digest 扩建前重新确认常见工具语义 | 在 Provider lockdown 前先确认时间范围 |
| 按 head 的状态台账 | 保留局部验证边界 | 旧 live run 不冒充新 head，CI 不冒充 review | 旧 open minor 不被近期无评论覆盖 |
| 外部阻塞停止 | 不适用 | 避免额度空转和损坏恢复上下文 | 避免权限/CI 重复催促 |

这些门槛能显著提前暴露问题，但不能保证零返工；维护者仍可能改变产品合同。目标是让改变发生时只修改对应切片，而不是在庞大实现上反复返工。

## 9. 下次执行顺序

1. 写一句任务合同和完成口径。
2. 建验收覆盖总账，标出真实入口和不能遗漏的边界。
3. 评估爆炸半径；大合同先取得人类裁决。
4. 跑通最窄完整用户旅程，再补负例和恢复。
5. 对关键 guard 做 mutation check，保持 review 只读。
6. 对 bot 评论逐条复现、分级，不自动扩需求。
7. 按精确 head 更新证据和 PR 状态，旧证据不继承。
8. 外部条件未变化就停止空转，留下恢复点。
