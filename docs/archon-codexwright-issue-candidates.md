# Archon × codexwright 可改造 Issue 清单与三项实施方案

日期：2026-11-17

更新：2026-11-19。第 1 至 7 节保留为最初调研和方案快照，不代表当前 Issue/PR 状态；#5230 已实现的完整版本及维护者要求的精简方案见第 8、9 节。方案已记录，按用户新增目标继续在独立分支落实精简版、验证、提 PR 并更新 Issue；旧完整实现保留。

## 1. 范围与筛选结论

本文件只记录 Archon 当前开放 Issue 中，能够直接复用 codexwright 现有实现、适合进一步改造的候选项。没有创建或修改 GitHub Issue/PR，也没有修改 Archon。

筛选时的仓库状态：

- Archon 共 200 个开放 Issue，其中 162 个没有 assignee。
- 排除已有开放 PR 的工作，以及维护者已经认领的工作。
- 逐项复核本清单候选的 assignee 和开放 PR 引用。
- 优先保留与 codexwright 的 Provider 配置、typed tools、权限、验证、材料输入、session、证据和恢复机制直接对应的方向。

最适合优先展开的三个 Issue：

1. [#5230](https://github.com/coleam00/Archon/issues/5230)：Script-backed typed tools。迁移价值最高，需要拆成 Provider 与 Engine 两部分。
2. [#5765](https://github.com/coleam00/Archon/issues/5765)：不可信文本的精确接受。安全边界清楚，与 codexwright 的审批和内容绑定高度一致。
3. [#5533](https://github.com/coleam00/Archon/issues/5533)：Dry-run 校验 wait 输入。改造范围明确，真实运行与 dry-run 可以共用同一验证器。

## 2. 完整候选 List

### 2.1 边界清晰、适合优先认领

| Issue | 可复用的 codexwright 能力 | 改造判断与注意事项 |
|---|---|---|
| [#5617](https://github.com/coleam00/Archon/issues/5617) Workflow validation accepts AI nodes whose provider cannot resolve | `sdk_capabilities()`、preflight、Provider 配置校验 | 让 validate 与 runtime 使用一致的 Provider 解析结果；脚本-only workflow 仍允许无默认 Provider，不需要真实模型调用。 |
| [#5551](https://github.com/coleam00/Archon/issues/5551) Workflow fixture reports expose credential-bearing stub diagnostics | `has_secret`、证据脱敏、受限诊断输出 | 做小型安全诊断投影，过滤输入对象 key、JSON Pointer 编码 key 和非法 JSON 片段；不改变 fixture verdict 和失败节点身份。 |
| [#5533](https://github.com/coleam00/Archon/issues/5533) A dry run does not check what a wait receives | 验证器复用、Gate 输入输出合同、失败证据 | 真实 pause 与 dry-run 共用 wait 校验；dry-run 不发模型请求、不写持久状态，但必须展示实际 question/options/recommendation/labels。 |
| [#5656](https://github.com/coleam00/Archon/issues/5656) A node can name a skill as optional | Skill 生命周期、显式加载、缺失可见性 | 复用 optional MCP 的形式与语义；缺失时继续运行并记录 absence，未声明的 Skill 仍不可用。 |
| [#5678](https://github.com/coleam00/Archon/issues/5678) A workflow input can be read from a file on workflow run | 材料导入、冻结输入、路径与大小限制 | 支持大文件输入，避免命令行长度限制以及 shell history/process list 泄露；路径必须显式声明，不能猜测。 |
| [#5479](https://github.com/coleam00/Archon/issues/5479) CLI: let `workflow run` name the persist_session scope | Thread/session 状态、独立 state dir、session fork | 相同 scope 的后续运行 fork 先前 session；不同 scope 和无 scope 保持现状；并发运行不能写同一对话。 |

### 2.2 价值较大、适合作为专项改造

| Issue | 可复用的 codexwright 能力 | 改造判断与注意事项 |
|---|---|---|
| [#2797](https://github.com/coleam00/Archon/issues/2797) Codex Gateway 配置 | `runtime_home()`、`model_network()`、endpoint 与凭证环境校验 | 有 `archon-needs-contract`。维护者已明确：Gateway 属于 Provider 配置与 credential vault，不属于 alias。不能按旧标题直接把 `baseUrl` 放进 alias。 |
| [#5657](https://github.com/coleam00/Archon/issues/5657) Clean Eval 环境 | 私有运行配置、禁用 ambient capabilities、环境白名单 | 维护者明确要求使用 Provider 自有配置，不新增 Archon 开关、不替换 Provider Home；run 记录实际 guidance sources。 |
| [#5230](https://github.com/coleam00/Archon/issues/5230) Script-backed typed tools | `tool_server.py` 的 Schema、权限、沙箱、超时和真实 receipt | 核心迁移项。Codex nativeTools 与 Workflow 工具声明、执行和 receipt 持久化分层实施，不能全塞进 Provider。 |
| [#5765](https://github.com/coleam00/Archon/issues/5765) 不可信文本经接受后才能进入 Agent | 非可信输入降权、精确内容 Hash、人工审批绑定 | 审批必须绑定精确文本版本，文本变化即失效；检查发生在任何 Agent 读取之前，后续 run 仍需复查。 |
| [#5793](https://github.com/coleam00/Archon/issues/5793) Usage/Cost 覆盖范围可见 | Token 分项、`unmeasured_turns`、`usage_incomplete`、未知值不填零 | 按节点列出 recorded/missing/partial 及原因；不能把缺失用量估算成实际成本。 |
| [#5735](https://github.com/coleam00/Archon/issues/5735) Sandbox 支持 run-scoped 路径 | `sensitive_paths()`、read/write roots、运行前权限快照 | 在节点启动时解析 worktree、git common dir、main checkout；记录最终 sandbox Profile，Container 另归 #4640。 |

### 2.3 匹配但建议后置

| Issue | 可复用的 codexwright 能力 | 后置原因 |
|---|---|---|
| [#5575](https://github.com/coleam00/Archon/issues/5575) Build/workflow provenance | Spec Hash、配置快照、Thread/Turn ID、恢复历史 | 跨 Engine、CLI、Web 和持久化，适合在 Provider 证据模型稳定后做；部分版本/commit 工作不能替代完整 workflow provenance。 |
| [#5605](https://github.com/coleam00/Archon/issues/5605) 修改 Pack 后从失败节点恢复 | Spec 修订、快照、精确提案、恢复语义 | 必须明确旧节点结果继续有效、新节点使用新 source；不是简单替换 digest，需处理节点删除或重命名。 |
| [#5341](https://github.com/coleam00/Archon/issues/5341) Dry-run 支持多轮 Loop | 有界循环、分轮 fixtures、退出条件与最大轮数验证 | 需要让 fixture 每轮提供不同 stub，并覆盖永不满足退出条件的情况；可与 #5533 后续共用 dry-run 语义。 |
| [#3140](https://github.com/coleam00/Archon/issues/3140) Artifact 区域评论进入 Gate | 分页 diff 审阅、审批绑定精确 proposal hash | 与 codexwright 的精确审阅高度匹配，但包含较多 Web/UI 与结构化评论工作。 |
| [#1960](https://github.com/coleam00/Archon/issues/1960) 展示父子 run tree | 父子 Thread/Run 血缘、工具与恢复证据 | 适合在 #5673 的 Codex 子 Agent 关系统一后做，避免重复建设血缘模型。 |

## 3. 不纳入本次候选的已有工作

| Issue/PR | 当前处理方式 |
|---|---|
| [#3478](https://github.com/coleam00/Archon/issues/3478)、[#3138](https://github.com/coleam00/Archon/issues/3138)、[#3647](https://github.com/coleam00/Archon/issues/3647)、[#2815](https://github.com/coleam00/Archon/issues/2815)、[#2746](https://github.com/coleam00/Archon/issues/2746) | 已分配给 Wirasm，不按“无人认领”处理。 |
| [#4935](https://github.com/coleam00/Archon/issues/4935) | Codex correction 已由 [#5879](https://github.com/coleam00/Archon/pull/5879) 合并；剩余 schema 分类/retry 由 [#5878](https://github.com/coleam00/Archon/pull/5878) 跟进，不重复实现。 |
| [#5673](https://github.com/coleam00/Archon/issues/5673) | 已有 [#5873](https://github.com/coleam00/Archon/pull/5873) 综合实现并包含 [#5675](https://github.com/coleam00/Archon/pull/5675) 的贡献，优先 Review/真实运行验证。 |
| [#5871](https://github.com/coleam00/Archon/issues/5871) | #5673 的后续跟踪项，不另开同类工作。 |

## 4. 三项选择的具体理由

### #5230：能力复用最完整

codexwright 已有可运行的声明式工具注册、输入输出 Schema、权限判断、写操作审批、进程边界、沙箱、输出限制和 receipt 校验。该 Issue 能把这些能力转成 Archon 的通用工具合同，价值高于单纯修一个 Provider 字段。实施必须拆层，避免把 Engine 职责误放进 Codex Provider。

### #5765：安全语义最清晰

该 Issue 已有明确的攻击路径和不变量：不可信文本不能先由 Agent 判断安全性，必须由可信人接受精确文本；后续读取还要重新验证。codexwright 的非可信输入、精确 hash 和一次性审批模型可以直接用于设计，不需要先发明一套新框架。

### #5533：最小改造即可消除真实验证盲区

当前 dry-run 已验证节点输出，却没有验证 wait 的接收内容，导致 fixtures 通过而真实运行才暴露非法 ask。该问题边界单一，关键是复用真实 wait 的校验 owner，而不是再复制一套 dry-run 校验。适合与 #5230、#5765 并行推进。

## 5. 三项详细实施方案

以下方案均为设计记录，尚未创建 Issue、修改代码或执行 Archon 联调。

### 5.1 #5533：Dry-run 与真实运行共用 Wait 接收内容校验

Issue：https://github.com/coleam00/Archon/issues/5533

#### 当前状态与精确缺口

- Issue 仍为 open，无 assignee，未发现引用该 Issue 的开放 PR。
- 真实运行由 `armAttention()` 组装 ask，由 `resolveAttentionDeclaration()` 校验 options/recommendation/other；底层规则由 `attentionOptionsSchema` 和 `attentionDeclarationProblem()` 持有。
- 当前 dry-run **已经部分实现校验**：有答案 stub 时，`stubAnswerOutput()` 会调用 `resolveAttentionDeclaration()`，现有测试也覆盖动态 options 非法和重复。
- 剩余缺口是：无答案 stub 时直接 paused，不校验 declaration；空 question 未按真实运行规则拒绝；labels 不解析、不展示；合法 ask 没有结构化 question/options/recommendation/labels 输出；校验仍依赖答案分支。

#### 最小改造路径

1. **提取纯 `resolveAttentionAsk()`**：放在 `dag/references.ts`，输入 nodeId、attention condition、nodeOutputs、render 回调；返回 message、options、recommendation、labels。只解析和校验，不生成 UUID、时间或 Store 记录。
2. **真实运行复用**：`armAttention()` 先调用纯 resolver，再添加 kind、waitingSince、pauseId、form、other、reaskedFrom 和 pauseFields。真实与模拟不再各写一套 ask 解析。
3. **dry-run 提前校验**：`simulateWait()` 在判断有无答案 stub 之前统一解析并验证 ask。随后有答案则验证答案并继续，无答案则 paused，但完整 ask 已输出。
4. **去掉重复解析**：`stubAnswerOutput()` 接收已解析的 options，不再第二次调用 declaration resolver。
5. **增加结构化 `attentionAsk` trace**：包含 form、options、recommendation、labels、other，保留现有 resolvedText 和答案 output。人类输出与 JSON schema 同步更新。
6. **增加窄的 labels fixture 断言**：例如 `wait-labels.<node>.<key>`，由 fixture-runner 将预期 labels 与实际解析值精确比较，不设计通用 ask 断言 DSL。

#### 输出与无副作用约束

- 非法 ask：dry-run `outcome=failed`，trace 指向 wait，reason 来自共享验证器；普通 `expect: completed` fixture 失败，负例可用 `expect: failed` 固定拒绝行为。
- 合法 ask：有 stub 时继续后续节点；无 stub 时保持 paused，但仍展示完整 ask。
- 共享 resolver 不调用 Provider、模型、数据库、pause/store/notice、定时器或事件订阅。
- 纯 stub dry-run 不创建 scratch worktree，不执行脚本，不改变现有 `exec-code` 隔离模型。
- Fixture 汇总报告继续保持窄投影，不默认扩散 attentionAsk 中的绑定值或敏感内容。

#### 可复用代码映射

| Archon owner | 复用方式 | codexwright 对应设计 |
|---|---|---|
| `dag/references.ts` 的 `resolveAttentionDeclaration()` | 继续作为 options/recommendation 的唯一语义校验入口 | `accept()` 在 WorkPacket 标记 passed 前重新校验实际输出 |
| `dag/nodes/wait/wait.ts` 的 `armAttention()` | 提取纯 ask resolver，真实 pause 与 dry-run 共用 | `structure_check()` 固定验证边界，避免模拟与真实规则漂移 |
| `attentionOptionsSchema`、`attentionDeclarationProblem()` | 不修改合法规则，只让 dry-run 也执行 | `verify_state()` 不信任已有状态字段，重新执行 acceptance |
| Fixture trace 与断言 | 对 labels 做结构化精确比较 | `expected_json` 要求实际 JSON 精确一致 |

这里复用的是验证所有权和证据合同，不是逐行翻译 Python。

#### 验收测试

每类非法声明至少覆盖“有答案 stub”和“无答案 stub”：

- recommendation 指向未提供的 option，报真实运行的 `names option ... which the wait does not offer`。
- 动态 options 出现重复 id，错误包含 producer、字段路径和 `declared more than once`。
- `other: true` 时动态 options 含保留字 `other`，与真实运行同样拒绝。
- 合法 question/options/recommendation：答案合法时下游继续，trace 精确包含全部字段。
- 合法但无答案：结果 paused，完整 ask 已输出，证明校验不依赖答案。
- 旧答案或 sibling 答案不能恢复当前 ask：answer 必须绑定当前 question/options/occurrence；真实运行已有的 stale-answer/re-ask 语义不能被 dry-run 改写。
- 静态与动态 labels：直接 dry-run 输出精确匹配；错误预期使 fixture 失败。
- 空 question：有无答案均在 wait 失败，使用真实运行的空问题错误。
- 无副作用：不创建临时目录，不调用 pause/store/notice/provider；现有 fixture 隐私与无 trace 测试继续通过。
- 每个负例都要真实断言失败原因，避免断言行位于异常抛出之后、测试只验证“有异常”而没有验证具体合同。

#### 不纳入范围

- 不改变 options、recommendation、other 的现有合法规则。
- 不改变真实 answer、resume、stale-answer、re-ask 语义。
- 不重构 attention queue、Web/CLI 展示或 labels 过滤。
- 不扩展 event/duration/until 的新规则，不自动修复 ask，不引入模型复核。
- 不涉及 Codex Provider 或其他 Engine 调度能力。

相关链接：[统一 attention 方向 #5480](https://github.com/coleam00/Archon/issues/5480)、[Pack 改造 #5529](https://github.com/coleam00/Archon/pull/5529)、[后续 ask 改造 #5530](https://github.com/coleam00/Archon/pull/5530)、[真实运行回归背景 #5520](https://github.com/coleam00/Archon/pull/5520)。

### 5.2 #5230：Script-backed Typed Tools 与权威 Receipt

Issue：https://github.com/coleam00/Archon/issues/5230

#### 当前状态与核心判断

- Issue 仍为 open，无 assignee，未发现关联开放 PR。
- 现有 `nativeTools` 已能把模型工具调用交给宿主 handler，主要服务 chat orchestrator；Workflow Agent 节点还没有“声明脚本工具 → NativeTool → 执行脚本 → typed receipt → 下游引用”的路径。
- **Provider 不需要重做协议通道，主要工作在 Workflow Engine。** Provider 负责协议翻译与工具事件，Engine 负责脚本、权限、超时、输出校验、持久化和引用。
- 当前 NativeTool 输入描述主要支持扁平 string/enum/boolean，handler 返回字符串。Codex、Claude、Pi 支持 nativeTools；不支持者必须在模型调用前拒绝。

#### codexwright 能力映射

| codexwright 现有实现 | 在 Archon 中的落点 |
|---|---|
| `ToolSpec` 的 name、input/output schema、side_effect、timeout、approval | AgentNode 的工具声明与静态校验 |
| `invoke()` 执行前输入校验 | Engine 在启动脚本前做权威校验，非法输入不得启动进程 |
| 权限与入口路径检查 | 绑定 run/node/attempt/tool 的权限与源码范围，不使用进程级总开关 |
| `bounded_output()` | 复用 Archon 现有 subprocess 的超时、输出上限与进程树终止，不移植 Python 实现 |
| 按 Agent 分配工具 | 每次 Agent attempt 只构造该节点声明的 `NativeTool[]` |
| `validated_tool_receipts()` | Engine 权威 receipt、输出 Schema 校验、call ID 和 typed artifact |
| `CodexRuntime.collect()` 收集真实工具证据 | 直接接 Archon 已有 `tool_call/tool_call_update` 事件流 |

不迁移 Python MCP server 整体、全局 `WORKFLOW_APPROVE_WRITES`、macOS/Linux 专用沙箱实现，也不要求每个声明工具必须被调用；是否调用由业务验收决定。

#### 最小合同

建议先支持命名脚本，复用现有脚本发现、源码捕获和 runtime 推导：

```yaml
- id: sweep
  prompt: merge-queue/commands/sweep.md
  tools:
    merge:
      description: "Guard and merge an accepted item"
      input_schema:
        type: object
        properties:
          item_id: { type: string }
        required: [item_id]
        additionalProperties: false
      output_schema:
        type: object
        properties:
          merged: { type: boolean }
          commit: { type: string }
        required: [merged, commit]
        additionalProperties: false
      script: merge-queue/scripts/gate.ts
      timeout: 60000
```

第一期 PR 可以只打通扁平 string/enum/boolean 的 Codex 垂直链路，但这只是实施切片，**不代表 #5230 已全部完成**。Issue 最终验收仍需覆盖维护的 Providers 和声明的 Schema 范围。

#### Provider slice：复用通道，补关联与类型

- 复用 Codex `buildCodexNativeTools()`、dynamic tool specs、turn/thread 校验、turn 结束后拒绝调用、`toolCatalogId()` 和 `dynamicToolCall` 事件映射。
- 增加标准 JSON Schema 子集到现有 NativeToolInputSchema 的转换，不另造一套平行的 chat schema。
- handler 返回字符串约定为一个完整 JSON 文档，由 Engine 生成；不要把文本响应伪称原生 structured output。
- 调用上下文必须携带 `providerCallId`，使 Provider 事件与 Engine receipt 精确关联，不能按工具名或输出文本猜测。
- `nativeTools: false` 时在模型调用前失败。Schema 变化必须改变 Codex catalog fingerprint，避免错误复用旧 Thread。
- Claude/Pi 复用各自 native tool 通道；Provider 不启动脚本、不拥有业务授权、凭证、输出校验或持久化。

#### Engine slice：主要实施步骤

1. **Loader/Schema**：AgentNode 保留 tools 字段，其他节点类型拒绝；校验工具名、重复定义、输入输出 Schema 和脚本来源。
2. **Attempt handler**：在构造 query options 时注入 nativeTools，闭包绑定 `runId/nodeId/attemptId/toolDeclaration`，不共享跨 attempt 的可变权限状态。
3. **共享脚本执行内核**：从 `executeScriptNode()` 抽取源码冻结、scriptInvocation、节点环境、ExecutionContext、超时、进程树终止、脱敏和输出上限；不要调用整个 script DAG 节点。
4. **权威 receipt**：先写 started，再执行，最后写 completed/failed/outcome_unknown。记录 `call_id/run_id/node_id/attempt_id/tool_name/provider_call_id/input_ref/output_ref/status/error`。
5. **输出与引用**：stdout 必须是完整 JSON 并通过 output_schema；完整结果保存 typed artifact，大内容用 artifact pointer。后续 Script 节点按 call ID 只读获取，不靠 regex 解析 Agent 文本。
6. **逐 Provider 验收**：Codex 打通后，用同一 Engine fixtures 验证 Claude/Pi；业务逻辑保持 Provider-neutral。

#### 安全与兼容约束

- Provider 可做协议形状校验，Engine 必须在进程启动前再做完整、权威输入校验。
- 工具声明不授予额外 MCP、Skills、Plugins、Shell、网络或写入目录权限。
- 使用节点原有 cwd/env/ExecutionContext；Codex 不支持容器执行时必须明确拒绝，不能回退 host。
- 需要审批时绑定具体 run、工具、输入和版本，不能用 `WORKFLOW_APPROVE_WRITES=1` 代替。
- 输入通道不能拼 shell 命令；必要时使用引擎私有输入文件或 argv。
- stdout/stderr 在返回 Agent 和持久化前必须脱敏并限长；原始输入优先保存引用，不默认落日志。
- 写工具超时、取消或记录缺失进入 `outcome_unknown`，禁止自动重放 merge/pay/send。
- 旧事件保持可读，新事件/artifact 采用 additive 方式；Engine 与 SDLC Pack 不互相 import。

#### 验收测试

Provider：

- Codex 合法调用到达 handler，JSON 结果进入 DynamicToolCallResponse。
- 伪造 sibling `tool_call_id`、HITL 恢复后原始调用 ID 丢失、同一审批被执行两次，都必须被拒绝或明确标记异常，不能拼成正常 receipt。
- MCP/content block list 等合法返回形状必须显式归一化，不能因响应类型不同而误判失败或重复执行。
- Claude/Pi 对同一 fixture 的合法与非法输入行为一致。
- 错误 thread/turn、未知工具、非法 namespace、Agent 已结束后的调用全部拒绝。
- 不支持 nativeTools 的 Provider 在模型调用前失败。
- Schema 变化改变 catalog fingerprint；resume 不丢失或错用工具。
- 不声明工具时，现有 chat 和 Workflow 行为不变。

Engine 正例：

- 声明工具实际执行，输出通过 Schema 并返回 Agent。
- started/terminal 记录、Provider 事件和 typed artifact 能按 call ID 关联。
- 后续 Script 节点读到同一逻辑 JSON。
- 工具继承节点环境、ExecutionContext、超时和权限。
- 大输出可截断展示，完整 typed artifact 仍可按权限读取。

必须覆盖的负例：

- 缺 required 字段、额外字段、错误类型、非法 enum、非对象输入：脚本启动次数为 0。
- 脚本非零退出、非 JSON、空输出、输出不符合 Schema。
- 超时且派生子进程：进程树被终止，不能写成普通成功。
- 输出超限或包含凭证：不得进入事件、日志或 Agent 响应。
- 脚本路径逃逸、符号链接逃逸、运行中替换源码。
- 未声明工具、跨节点工具、同名冲突、非法 Schema：加载或调用前拒绝。
- 写工具超时/取消/崩溃：禁止自动重放，记录 `outcome_unknown`。
- 持久化失败：不能把“模型说成功”记录成工具成功。
- 声明工具后不得出现额外 MCP/Skill/Plugin/Shell 能力。

#### 不纳入范围

- SDLC merge queue 的实际替换和旧代码删除，按 Issue 要求另开 removal issue。
- 通用人工审批 UI、支付/发送等外部事务协议和 exactly-once 外部副作用。
- 任意嵌套 JSON Schema、所有 `$ref`、跨版本 Schema 语义归一化。
- 通用 DAG、checkpoint/recovery、沙箱体系重写。
- 将 codexwright 的 ArchitectureSpec、Python MCP 或 Codex SDK 接入 Archon。
- Web 可视化编辑器和完整 Workflow 自迭代。

相关链接：[Provider NativeTool 合同](https://github.com/coleam00/Archon/blob/96678f0307ccfdb86027993c9a6b30b8485850a2/packages/provider-contract/src/agent-provider.ts)、[Codex native-tools](https://github.com/coleam00/Archon/blob/96678f0307ccfdb86027993c9a6b30b8485850a2/packages/providers/src/codex/native-tools.ts)、[Archon 边界规则](https://github.com/coleam00/Archon/blob/96678f0307ccfdb86027993c9a6b30b8485850a2/AGENTS.md)。最大待确认合同是各 Provider 的调用 ID 如何与 Engine 权威 receipt 精确关联。

### 5.3 #5765：不可信文本的精确接受与强制执行

Issue：https://github.com/coleam00/Archon/issues/5765

#### 当前状态与安全边界

- Issue 仍为 open，无 assignee，未发现关联开放 PR。
- 方案采用 **Engine 持有接受记录，Forge 提供身份与原文证据，Workflow admission/executor 强制执行**。不把信任判断塞进 predicates，也不新增 pack script。
- 可信人必须接受自己实际看到的 digest；不能收到 label webhook 后再读当前 body，并推定那就是维护者接受的版本。
- title 同样可能携带注入，建议首版共同绑定 `title + body`；若只保护 body，必须明确 title 通道的处理方式。
- 若 Agent 能用 gh、HTTP 等直接读取 issue，Engine 检查会被绕过。受保护模式必须关闭这些旁路，或统一经过 guarded forge read，否则不能声称覆盖“任何 Agent”。

#### codexwright 能力映射

| codexwright 现有实现 | 在 #5765 中的落点 |
|---|---|
| `normalize_materials` 的来源、`source_sha256`、冻结材料和漂移拒绝 | accepted snapshot 与 stale input 检查 |
| `approve(expected_proposal_hash)` 精确审批 | 可信人提交 `expectedContentDigest` |
| `finish_public_review` 的版本和并发冲突处理 | 接受记录的 CAS/幂等处理 |
| `apply` 执行前重新核对 hash、revision、snapshot | before-agent 与 later-run 复查 |
| `ExternalMessage` 非可信输入降权 | 接受后仍作为外部数据，不能变成系统指令 |
| Archon Pack 的 `bodyDigest/decideIntake/bodyMoved` | 将 digest、编辑后失效和 later-run recheck 移到 Engine 信任准入模块，不能 import pack |

codexwright approval 是一次性且会过期；文本接受则应在内容未变化时允许后续多个 run 复用，**靠 digest 失效，而不是用一次就消费**。

#### 数据合同

Trusted declaration 来自项目策略和 operator binding，不能来自 event inputs：

```json
{
  "schemaVersion": 1,
  "maintainers": {
    "source": "default_branch_file",
    "path": ".archon/sdlc/policy/maintainers.json"
  },
  "contentFields": ["title", "body"],
  "acceptance": {
    "kind": "trusted_item_acceptance",
    "expectedDigestRequired": true
  }
}
```

- 同时记录 `defaultBranchHead` 和 `policyDigest`。未启用 declaration 的旧项目保持现状；启用后策略缺失、损坏或不可读必须 fail closed。
- Acceptance 记录包含：`acceptanceId/projectKey/itemKey/subject/content.digest/sourceRevision/snapshotRef/acceptedBy/policy/acceptedAt/sourceReceiptId`。
- Digest 对固定字段顺序的原始字符串计算 SHA-256；不做 Unicode、CRLF、trim 等隐式规范化。跨 Forge 以 content digest 为准，不能只信 updatedAt。
- Event envelope 的 `sourceReceipt.contentDigest` 与 accepted text digest 不能混用；接受记录按 project + item + repo + subject 限定，不能跨项目重放。

#### 接受动作

可信人先看到文本和 digest，再提交 `accept(item, expectedContentDigest)`。Engine 原子验证并保存：

审批界面必须让接受者直接看到**实际文本及其 digest**，不能只显示一个笼统的 Continue/Approve 按钮。

1. 操作者来自 Forge 已验证身份，且在默认分支 HEAD 的 maintainer 列表中。
2. `expectedContentDigest == 当前文本 digest`。
3. 保存 snapshot 后重新计算仍等于 accepted digest。
4. 接受记录、actor、policy revision 和 snapshot 原子提交。

普通 label 只有在同一可信事件负载携带当时文本或 digest 时才能作为接受动作；否则必须要求显式 digest。

#### Before-agent 与 later-run 检查

- `prepareBinding`：在准备 AI 配置和 run admission 前检查，未接受则不准备 Agent 运行。
- Agent dispatch 前：再次验证 acceptedDigest/contentFields/itemKey，prompt 只能解析 acceptedTextRef。
- `admitWorkflowRun`：排队结束、图执行前重新读取当前 title/body、作者和默认分支策略，要求 currentDigest 等于 acceptedDigest，接受者仍满足当前策略。
- 后续节点只读 frozen accepted snapshot；节点前发现漂移则暂停。文本变化后状态回到 `waiting_acceptance`，新文本不得进入 run inputs、prompt、事件或 Agent 日志。

拒绝状态在 item/CLI/Web 可见：

```json
{
  "state": "waiting_acceptance",
  "reason": "content_changed_after_acceptance",
  "acceptedDigest": "sha256:...",
  "currentDigest": "sha256:...",
  "agentStarts": 0
}
```

同时保留 `untrusted_accept_refused`、`policy_unreadable` 等原因，只记录 digest 和身份，不记录未接受原文。

#### 分阶段改造

1. **合同与策略**：canonical content digest、trusted declaration reader、typed acceptance store、`accept(expectedDigest)`。
2. **准入与读取**：接入 `prepareBinding`、`admitWorkflowRun`，提供 guarded `workitem.view` 或 accepted snapshot resolver。
3. **覆盖入口**：webhook、trigger fire、手工 run、resume、子 run 都经过同一复查；接通 item/CLI/Web 等待状态。
4. **无脚本 Pack 验收**：用只有 YAML binding 的 Pack 完成接受、拒绝、编辑后等待，再补 workflow-triggers 和 forge 文档。

#### 必测攻击、竞态与负例

- 外部作者事件到达：Agent/Provider 调用数为零。
- 非 maintainer 接受、伪造 actor、跨 item/repo 重放 acceptance：全部拒绝。
- 人看到 D1，但接受前文本已变 D2：提交 D1 必须拒绝。
- D1 接受后、排队期间变成 D2：later-run 不启动 Agent。
- 只修改 title、CRLF 或 Unicode：同样使 digest 失效。
- 重复相同接受幂等；不同 digest 并发接受不能互相覆盖。
- Maintainer 被移除、策略文件损坏、默认分支不可读：fail closed。
- Resume、子 run、手工 trigger 不得绕过检查。
- 未接受文本不得出现在 run row、事件、日志和拒绝消息里。
- 直接 gh/HTTP 读取旁路必须被阻止，或明确判定该运行配置不满足受保护模式。
- 可信作者无需接受步骤，但后续 run 仍重新检查作者、策略和当前 digest。
- 无 declaration 的旧项目行为保持不变。

#### 不纳入范围

- 不让模型判断文本是否安全，不做自动清洗或自动重新接受。
- 不把接受文本提升为可信指令；权限和工具限制继续生效。
- 不混入 merge gate、通用 sandbox 或跨 Provider 改造。
- Comments、reviews 等其他文本通道在获得自己的 accepted revision 前，受保护 Agent 不得读取。
- 不支持“收到 label 后现读当前 body，再推定维护者接受了它”的兼容捷径。

相关链接：[Pack 迁移背景 #4438](https://github.com/coleam00/Archon/issues/4438)、[Item 映射前置 #5747](https://github.com/coleam00/Archon/issues/5747)。最大实现风险是 Forge 缺少可靠的接受时文本版本，以及 Agent 直接读取 Forge 的旁路。

## 6. 推荐实施顺序

1. **#5533**：先建立真实/模拟共享验证的小闭环，为后续 typed tools 和 trust gate 提供 fixture 验证思路。
2. **#5765**：优先落实 before-agent 的强制边界，再覆盖 later-run、旁路和所有启动入口。
3. **#5230**：按 Provider channel → Engine executor → receipt → downstream reference 分层推进，最后用 SDLC 自有场景验收。

三项可并行设计，但实现上不要把它们合并成一个大 PR。#5230 的 Codex 垂直切片不等于 Issue 全部完成；#5765 只有同时处理直接读取旁路，才能声称满足其安全目标。

## 7. 公开社区问题证据与方案修正

本节补充公开 GitHub Issue 检索结果，避免方案只参考 codexwright。检索范围包括 LangGraph、AutoGen、MCP Servers 和 GitHub MCP Server。

### 7.1 Typed Tools：调用关联、返回类型和重复执行

- [LangGraph #7989](https://github.com/langchain-ai/langgraph/issues/7989)：ToolNode 接受绑定到 sibling `tool_call_id` 的伪造 ToolMessage，证明仅校验工具名和输出不够，调用 ID 必须精确关联。
- [LangGraph #8304](https://github.com/langchain-ai/langgraph/issues/8304)：HITL 恢复需要原始 `tool_call_id` 重建 ToolMessage，直接支持本方案的 `providerCallId`。
- [LangGraph #9676](https://github.com/langchain-ai/langgraph/issues/9676)：并发写入竞态导致已批准工具再次审批、执行两次或审批消失，证明 `outcome_unknown` 和禁止盲目重放是硬要求。
- [LangGraph #7985](https://github.com/langchain-ai/langgraph/issues/7985)：MCP content block list 归一化失败，说明 typed output 需要显式支持多种合法响应形状。
- [MCP Servers #3752](https://github.com/modelcontextprotocol/servers/issues/3752)：路径参数缺乏约束导致 Prompt Injection 可诱导读取 SSH 私钥，证明 Schema 合法不等于权限安全。

因此，#5230 的验收新增三项硬约束：伪造/错配调用 ID 不得形成 receipt；HITL 恢复不得重复或丢失审批执行；合法 content block list 必须正确归一化。第一期扁平 Schema 仅是实施切片，不是最终工具合同。

### 7.2 不可信文本：已有真实泄露与权限提升案例

- [GitHub MCP Server #844](https://github.com/github/github-mcp-server/issues/844)：公开 Issue 中的 Prompt Injection 导致 Agent 把私有仓库内容发布到公开仓库，与 #5765 的攻击路径高度一致。
- [AutoGen #7457](https://github.com/microsoft/autogen/issues/7457)：网页 `<title>` 可直接注入指令，证明 title 也是必须处理的注入通道。
- [AutoGen #8238](https://github.com/microsoft/autogen/issues/8238)：Peer Agent 的 `HandoffMessage.context` 可把 SystemMessage 原样注入另一个 Agent，证明接受后的外部内容也不能提升为系统指令。
- [MCP Servers #5151](https://github.com/modelcontextprotocol/servers/issues/5151)：社区明确建议读取结果携带来源路径和 `untrusted` 标记，对应来源和信任级别记录。

因此，#5765 保留 `title + body` 共同绑定，接受后的文本仍按外部数据处理；审批界面必须展示实际文本和 digest，不能只提供笼统 Continue。直接 gh/HTTP 旁路必须有明确拒绝测试。

### 7.3 Dry-run/HITL：旧答案、错配和测试失效

- [LangGraph #8837](https://github.com/langchain-ai/langgraph/issues/8837)：已消费 resume 值再次投递，导致后续 interrupt 被旧答案自动回答。
- [LangGraph #8579](https://github.com/langchain-ai/langgraph/issues/8579)：多个 interrupt 等待时标量 resume 被错误接受，说明答案必须绑定明确 interrupt。
- [LangGraph #9106](https://github.com/langchain-ai/langgraph/issues/9106)：恢复一个并行 interrupt 时另一个已完成节点被重新执行，说明恢复边界不能只按节点名判断。
- [LangGraph #9161](https://github.com/langchain-ai/langgraph/issues/9161)：断言位于 `pytest.raises` 内成为死代码，证明有测试不等于验证了具体合同。

因此，#5533 在原有 Schema 校验之外增加 answer-to-ask identity 测试：答案必须对应当前 question/options/occurrence，旧答案或 sibling 答案不能恢复当前 ask；每个负例必须实际断言具体失败原因，而不是只断言发生异常。

这些公开案例与 codexwright 的实现共同支持同一结论：工具调用必须精确关联，接受必须绑定内容版本，失败不得盲目重放，真实与模拟必须共享验证器。

## 8. #5230 完整实现存档：PR #5897 重版

### 8.1 存档身份和证据边界

- 记录日期：2026-11-18。
- Issue：<https://github.com/coleam00/Archon/issues/5230>。
- PR：<https://github.com/coleam00/Archon/pull/5897>。
- 完整实现分支：`codex/issue-5230-typed-script-tools`，fork 为 `Jack-mi/Archon`。
- 已核对的完整实现提交：`a35802f8c57425dac2b26d41e6fb669a62da6ce1`。
- 本地完整实现：`/tmp/archon-issue-5230`，本次检查时工作区干净，HEAD 与 PR head 一致。
- 精简版设计参考的上游：`dev@3e4ff4f1d0de1c293b84b2ae30f15652fa2f10a1`；开始实现前再次 fetch，不假设上游停在此处。
- GitHub 当前 diff 统计为 37 个文件、2163 行新增、56 行删除。这是特定 base/head 的差异，不是运行质量或性能指标。
- 本节依据实际代码记录，区分现有实现与第 9 节的未实现方案，不把最初设想写成已具备能力。

完整代码已经保存在上述提交。后续精简不覆盖这条分支、不 amend、不 force-push；需要恢复时从该提交创建独立分支。以下命令用于查看原实现，不执行外部业务动作：

```bash
git -C /tmp/archon-issue-5230 show a35802f8c57425dac2b26d41e6fb669a62da6ce1
git -C /tmp/archon-issue-5230 show a35802f8c57425dac2b26d41e6fb669a62da6ce1:packages/workflows/src/dag/nodes/agent/script-tools.ts
```

### 8.2 完整版目标与调用链

完整版提供 Agent 调用声明式命名脚本的路径，并把执行、Schema 校验、关联身份、持久化和重放约束交给 Engine，不放进 Codex Provider。

```text
AgentNode.tools
  -> Loader 保留声明，能力检查确认 nativeTools
  -> pack 内命名脚本 qualification
  -> 为每次 Agent attempt 构造 NativeTool[]
  -> Provider 接收模型工具调用，携带调用 ID/连接 scope
  -> Engine 校验输入、读取历史调用
  -> 写输入 artifact 和 started receipt
  -> 复用脚本发现/冻结源码/运行环境执行 subprocess
  -> 校验 stdout JSON 与 output_schema
  -> 写输出 artifact 和 completed receipt
  -> 返回 JSON 给 Agent
  -> 后续脚本通过 TOOL_CALLS_FILE 读取调用结果
```

不声明工具的节点保持原执行路径。工具的选择、调用次数和业务判断仍由 Agent 决定；声明并不要求 Agent 调用每个工具，也不授予额外 ambient MCP、Skills 或 Plugins。

### 8.3 当前 YAML 与输入合同

Agent 节点 `tools` 是工具名到声明的映射，每项包含：

```yaml
tools:
  record:
    description: Record a checked finding
    input_schema:
      type: object
      properties:
        value: { type: string }
      required: [value]
      additionalProperties: false
    output_schema:
      type: object
      properties:
        recorded: { type: boolean }
      required: [recorded]
      additionalProperties: false
    script: record
    timeout: 60000
```

- 工具名以字母开头，只允许字母、数字、下划线和短横线，最长 64 字符，禁止空工具集合。
- `script` 必须是命名脚本，非命名字符串不能意外按 inline Bun 代码执行。
- pack qualification 与普通命名资源一致，避免 pack-local 工具错误运行同名 shared 脚本。
- 当前输入只能是扁平 object，属性支持 string、string enum、boolean；数字、嵌套对象、数组和其他未支持关键字会被输入转换器拒绝。
- Engine 用现有 `compileOutputSchema` 和 `validateStructuredOutput` 再验证实际输入、输出，非法输入不启动脚本。
- 当前没有 `writes` 声明。所有工具共用同一套保守副作用治理，这是维护者要求修改的主要原因。

### 8.4 Provider 接入与调用身份

共同合同位于 `packages/provider-contract/src/agent-provider.ts`：`NativeTool.handler(input, context)`，context 携带 `providerCallId`，可携带 `providerCallScope`。

| Provider | 当前接入与身份 |
|---|---|
| Codex | dynamic tools；校验 thread、turn、namespace 和工具名；实际 `callId` 传给 Engine。 |
| Claude | SDK 内 MCP server；MCP `requestId` 是连接局部 ID，所以另生成每个 server 的 scope，避免重连 ID 复用造成旧结果误重放。 |
| Pi | customTools / defineTool；`toolCallId` 传入 Engine。 |
| Provider plugin | serve、wire、connect 保留 call ID 和可选 scope；已同步生成 provider-contract schema。 |

当前能力检查会在模型调用前拒绝 `nativeTools: false`。Claude scope 并不等于模型可见的 `tool_use_id`；完整版没有宣称两者严格等同。

### 8.5 脚本执行与隔离

- `prepareNamedScript` 复用脚本发现、pack 名称、captured source 校验、Bun/Python runtime、脚本环境和 stdin 处理，不调用整个 DAG script node。
- 输入经 `ARCHON_TOOL_INPUT` 传递，调用标识经 `ARCHON_TOOL_CALL_ID` 传递；不把模型输入拼进 TS、Python 或 shell 源码。
- 复用现有 subprocess 超时、输出上限、日志保留、凭证脱敏和进程树处理。
- run-stop signal 与 Agent attempt signal 合并；Agent 失败时先 abort，再等待 in-flight tools 结束，避免失去生命周期所有权。
- Provider stream 没有 settled 时，先取消工具，再报告原始 Provider 错误；不能用内部 abort 冒充用户取消。
- 当前显式拒绝 provider sandbox 与 container-backed script tools，因为原实现不能保证 Engine 工具受到同样 sandbox/取消治理。

这些专用 refusal 和工具生命周期处理不属于普通 script node 的全部默认行为，也是精简版要求删除或复用的部分。

### 8.6 Receipt、artifact 与历史重放

`workflow_tool_call` 是状态转换事件，而不是每次调用只有一条记录。当前调用通常先 recorded `started`，再 recorded `completed`、`failed` 或 `outcome_unknown`。

调用数据包含：

```text
call_id / run_id / node_id / node_path
attempt_id / invocation_id / loop_path
tool_name / provider_call_id / provider_call_scope
input_ref / input_digest
output_ref / output_digest
status / error / recorded_at
```

- 原始输入、输出写入 Engine 私有 artifact，receipt 主要保存引用，文件权限为 0600。
- 输入、输出带 SHA-256；重放和后续 listing 读取检查 artifact 是否存在、字节是否匹配、JSON 是否可读。
- `foldToolCalls` 按 call ID 汇总最新转换，拒绝不同 run、错误路径和冲突 terminal transitions。
- 当前 attempt 初始化时读取历史；同节点/调用身份的 completed receipt 可返回原结果，不重新执行脚本。
- 连接 scope + Provider call ID 用于区分实际 invocation，不按工具名或自然语言内容猜测身份。
- 历史 started / outcome_unknown 阻止继续执行；前次 attempt 已完成写入但出现新 Provider 调用时也保守拒绝，而非猜它与旧调用等价。
- 当前 attempt 内同 ID、同参数调用共享结果；同 ID、不同参数拒绝。

这套机制能减少盲目重放，但把普通查询也纳入相同治理，并增加了状态、artifact 和恢复代码。

### 8.7 失败处理的当前真实语义

| 失败阶段 | 完整版处理 |
|---|---|
| 非法输入 | 在进程前拒绝，无输入 receipt、无副作用。 |
| 明确未启动的 spawn 失败 | 普通 failed tool receipt，不视为已执行的未知动作。 |
| 进程启动后非零退出、被信号杀死、超时、取消 | 保守 `outcome_unknown`。 |
| stdout 不是 JSON、输出 Schema 不匹配 | 进程已运行，视为未知结果，不向后续节点提供成功输出。 |
| artifact/receipt 无法保存或历史完整性检查失败 | 设置 unknown 状态，不能把失败当作成功。 |
| 工具已 unknown、Provider 又失败或无输出 | 保留原 Provider message/kind，同时强制 `retryable: false`。 |

当前 unknown 状态是 attempt 级阻断标记：后续工具不能再开始；Agent 即使捕获工具错误也不能让节点成功。该标记会在异步准备之后、实际 subprocess dispatch 之前再次检查，防止并发准备竞态。

### 8.8 后续节点消费与改动清单

完整版新增 `TOOL_CALLS_FILE`，由 invocation listing 生成调用清单，并在可执行节点环境暴露。下游不是通过 `$agent.output` 读取，而是沿独立 listing/artifact 路径读取和重新验证结果。

| 模块 | 当前完整实现文件 |
|---|---|
| 声明与 Loader | `schemas/provider-options.ts`、`dag-node-base.ts`、`node-normalize.ts`、`node-ignored-fields.ts` |
| 能力与模型分配 | `validator/capabilities.ts`、`dag/capability-preflight.ts`、`dag/provider-resolution.ts` |
| 工具主运行时 | `dag/nodes/agent/script-tools.ts`、`dag/nodes/agent/agent.ts`、`dag/ai-turn.ts` |
| 共享执行 | `dag/nodes/exec/script.ts`、`dag/run-control.ts` |
| 持久调用和 artifact | `schemas/tool-call.ts`、`tool-calls.ts`、`store/event-types.ts` |
| 独立消费路径 | `invocation-listings.ts`、`exec-environment.ts`、`dry-run/nodes/exec.ts` |
| Provider 和插件 | `provider-contract/src/agent-provider.ts`、`plugin/{serve,wire,connect}.ts`，Codex/Claude/Pi native-tools |
| Pack 与文档 | `packaged-workflow.ts`、workflow-language reference |
| 主要测试 | `script-tools.test.ts`、`packaged-workflow.test.ts`、Provider native-tool conformance、plugin round-trip、workflow-variables |

该清单中的 Workflow 文件路径均相对 `packages/workflows/src/`，Provider 文件相对各自 package，完整代码以 8.1 固定提交为准。

### 8.9 既有验证与维护者反馈

前序提交验证过：30 个 script-tool 聚焦用例、Agent + terminal-output 115 个回归、provider-contract 261 个测试、Provider 套件以及类型、lint、schema、ratchet 等检查。它们是既有提交的历史验证，本次仅检查方案和源码，没有重跑，不写成精简版验收结果。

既有测试覆盖非法输入零启动、pack-local 解析、各 Provider 调用、重放、并发 unknown、取消/超时/signal、Provider 未 settled、历史 artifact 篡改、输出不确定及不可重试。缺少真实计费模型 E2E；container 被明确拒绝，不能写成已支持容器。

维护者 2026-11-18 17:39（Asia/Shanghai）的新回复：<https://github.com/coleam00/Archon/pull/5897#issuecomment-6974718215>。

他认可声明、Provider/Engine 分层、调用 ID 和输入校验，但不愿合并当前重版；认为普通查询和检查会更常见，而现有设计把每个工具都当成不可逆写入。他要求删除普遍重放、digest、防篡改和过量 latch/drain，改为第 9 节的轻量调用合同。这是产品与架构取舍，不是再加几个测试就能解决的缺陷。

## 9. #5230 精简方案：普通工具默认轻量，写工具显式治理

### 9.1 交付目标与实施边界

提供最小完整链路：Agent 声明命名工具，Provider 传递调用，Engine 校验输入并按普通 script node 执行，返回结构化结果，记录每次调用，后续节点沿已有输出路径消费。

用户已要求方案梳理后完整落地。在最新 `dev` 创建独立 `codex/issue-5230-script-tools-lite` 分支，实施目录为 `/tmp/archon-issue-5230-lite`；保留 #5897 与原完整分支，精简版验证与新 PR 就绪后再关闭旧 PR，不提前删除或覆盖完整实现。

### 9.2 保留、调整和删除

| 处理 | 明确范围 |
|---|---|
| 保留 | `tools` 声明；命名脚本；pack qualification；Provider call ID；plugin wire 传递；nativeTools 能力预检；Engine 权威输入输出校验。 |
| 调整 | JSON Schema 支持数字、嵌套对象、数组；普通工具失败返回 Agent；`writes: true` 才启用未知写入的非重试规则；复用 script node 的执行、隔离、超时和取消合同。 |
| 删除 | historical replay、replayOnly、digest、typed call artifacts 和重新验证、独立 `TOOL_CALLS_FILE`、started/terminal 多状态事件流水、对所有工具生效的 unknown latch。 |
| 不新增 | 新工作流引擎、通用审批 UI、exactly-once 框架、容器专用 kill 机制、自动业务拒绝语义解析、整个 SDLC Pack 的迁移。 |
| 不能删除 | 未知写入阻止盲目重试、Schema 验证、命名脚本边界、凭证脱敏、已有执行隔离与错误处理。 |

### 9.3 新工具声明

```yaml
- id: inspect
  prompt: Inspect the item and decide whether to proceed
  tools:
    lookup:
      description: Read the item and its checks
      script: lookup-item
      input_schema:
        type: object
        properties:
          item_id: { type: integer }
          include:
            type: array
            items: { type: string }
          filters:
            type: object
            properties:
              only_open: { type: boolean }
            additionalProperties: false
        required: [item_id]
        additionalProperties: false
      output_schema:
        type: object
        properties:
          checks_green: { type: boolean }
        required: [checks_green]
        additionalProperties: false
    publish:
      description: Publish a checked result
      script: publish-item
      writes: true
      input_schema:
        type: object
        properties:
          item_id: { type: integer }
        required: [item_id]
        additionalProperties: false
      output_schema:
        type: object
        properties:
          decision: { type: string, enum: [published, refused] }
        required: [decision]
        additionalProperties: false
```

- `writes` 默认 false；由 operator-authored YAML 决定，模型参数、脚本返回值或检索文本不能把工具改成可写工具。
- `writes: false` 是业务声明，不是操作系统保证只读；脚本权限仍由项目和已有 ExecutionContext 管理，错误标注写脚本有明确风险。
- 保留工具 timeout，但使用现有 script 执行的定义，不再派生独立生命周期策略。
- function tools 的顶层参数仍为 object；数字、数组、嵌套对象作为属性值支持，不把“支持数字”误写成所有 Provider 都支持顶层标量参数。
- 业务检查未通过可以返回合法 JSON `{ "decision": "refused" }`；Engine 验证形状，不解析或强制解释这段业务内容。

### 9.4 输入 Schema：不能只删 Engine 的扁平转换器

当前上游 `NativeToolInputSchema` 本身仍是扁平 string/enum/boolean；Claude、Codex、Pi 和 plugin wire 都依赖它。只修改 Workflow 输入校验，会让复杂参数在 Provider 边界先被拒绝，功能仍无法实现。

建议一次性扩展共同合同：

1. 保留已有 chat tools 的扁平输入声明与 `defineNativeToolInputSchema`，避免全仓无关迁移。
2. 在同一 NativeTool 合同添加可区分的 JSON Schema 形式，例如 `{ jsonSchema: <object schema> }`；不是新增一个可与 inputSchema 冲突的平行可选字段。
3. 旧形式可归一化为标准 JSON Schema；新形式直接保留作者声明。能力描述、Codex catalog fingerprint、plugin wire/schema 同步覆盖该分支。
4. Engine 输入、输出都调用现有 `compileOutputSchema` / `validateStructuredOutput`；校验失败不启动脚本。不要另写业务 JSON Schema 验证器。
5. Provider 只翻译 SDK 需要的表示：Codex dynamic tools 接收 JSON Schema；Claude 需要 SDK/MCP 可接受的 schema 表示；Pi 使用现有 TypeBox 接口承载 schema。数字、数组和嵌套对象要在真实通道里验证，不能只测 Engine。
6. Claude 的 JSON Schema 到 Zod 转换优先使用已安装依赖具备的能力；官方 `z.fromJSONSchema` 属于 experimental，实施前检查锁定版本和关键字保真，不能把一次转换成功写成支持任意 Schema。来源：<https://zod.dev/json-schema>。
7. `validateStructuredOutput` 还带 reserved metrics 校验；实施时检查工具参数是否误触发这条节点输出规则，不因为复用 validator 引入无关输入约束，也不删除原 metrics 不变量。

最低覆盖 string、enum、boolean、number/integer、array、nested object；其他关键字遵循现有 validator 的可编译合同及 Provider 的真实能力。无法安全转换的声明在模型花费前明确拒绝，不能静默丢关键字。

### 9.5 执行内核：一个 owner，两个调用方

从现有 script node 拆出最小共享执行函数，返回解析/执行结果，不产生第二个 DAG 节点、不额外写 node_started/node_completed。

```text
executeScriptNode -> 共享脚本准备与 subprocess 执行 -> 原节点结果/持久化
Agent tool handler -> 同一共享执行 -> 工具结果/一条调用事件
```

共享范围：命名发现、captured source、runtime、cwd、ExecutionContext、环境、stdin、timeout、stdout/stderr、输出限制、凭证保护和取消结果。保留现有脚本模块的错误分类，不重新复制一套脚本运行器。

- 工具与 script node 使用同一 container 能力；不继续保留 `tools cannot run in a container` 等专用拒绝列表。
- 支持与不支持都跟随当前 script node 的实际实现；不能为满足文档声称容器取消已保证终止，也不在此 PR 重写容器执行体系。
- Provider sandbox 是 Provider 自己的边界，不能宣称它自动保护 Engine 启动的 subprocess；按 script node 的现有隔离语义明确记录执行位置。
- 复用 script runtime 的失败输出，按工具声明校验 JSON；业务正常拒绝和真正的脚本错误都返回可读反馈。

### 9.6 普通失败与未知写入的决策表

| 调用结果 | 普通工具 | `writes: true` |
|---|---|---|
| 输入非法、命名脚本不存在、明确 pre-start spawn 失败 | 返回 tool error，Agent 可继续，无 subprocess 副作用。 | 同样返回 tool error，不凭空标记 unknown。 |
| 合法 JSON 的业务拒绝 | 返回 output，由 Agent 理解和决定后续行为。 | 同样返回 output；Engine 不把 `refused` 单词当作恢复协议。 |
| 正常可观察的脚本失败 | 返回 tool error，不直接失败 Agent node。 | 保留失败反馈；不能把所有失败一律提升为未知写入。 |
| 输出不是 JSON或不符合 Schema | 返回 tool error，不伪造成功。 | 能证明确定执行结果时返回 tool error；执行已发生且无法确认结果时按 unknown write 处理。 |
| 执行中超时、取消、signal/process/transport 中断，写入结果无法确认 | 返回 tool error，沿原 Agent/run 生命周期退出，不扩大成写入恢复框架。 | 记录 outcome_unknown，阻止本 attempt 发起新写入，节点失败且 `retryable: false`。 |
| 已得到结果，但调用事件无法保存 | 暴露记录失败，绝不声称记录成功；使用既有 store error 处理。 | 写入已发生但无法保留观察证据时保守拒绝自动重试，不让结果丢失变成隐式重做。 |

判断依据是共享运行器提供的结构化执行事实，不解析 stderr 的自然语言来猜“是否写成功”。明确的非零退出只证明进程失败，不自动证明业务绝无副作用；写脚本应以 schema-valid 结果报告业务拒绝，无法确认的中断必须保守处理。

只保留写工具需要的最小安全状态和收尾：当前 attempt 的 outstanding write 调用集合、一个 unknown-write 标记及节点结束前的最小收尾。取消/确认结束复用已有 runtime，不给每个普通查询创建一套历史 receipt 状态机。

禁止自动节点重试与 Agent 主动发起新的工具调用是不同语义。unknown write 后两者都不能悄悄再次执行同一个写入；不用重放旧结果、不把未知结果返回成已成功。

### 9.7 每次调用一条事件

建议调用完成或得到失败/unknown 观察后记录一条 `workflow_tool_call`。保持 Engine 生成事件，不把模型 prose 当 receipt。

```json
{
  "run_id": "run-id",
  "node_id": "inspect",
  "attempt_id": "attempt-id",
  "provider_call_id": "actual-call-id",
  "provider_call_scope": "optional-transport-scope",
  "tool_name": "lookup",
  "writes": false,
  "status": "completed",
  "input": { "item_id": 7 },
  "output": { "checks_green": false },
  "error": null
}
```

- call ID + attempt/transport scope 只用于当前真实调用关联，不再索引历史 completed calls 进行重放。
- 不写额外 started receipt，不需要 input_ref/output_ref/digest，不新增 call listing 文件。
- 错误事件与成功事件都能携带结构化 input/output；只有输出实际存在时才记录 output，不制造空成功对象。
- 输入、输出、错误经过现有脱敏及大小限制后才能持久化；原始凭证不进事件。大内容沿已有 artifact pointer 合同处理，不重建专属 tool artifact 管理。
- 该事件是已观察调用结果，不是 durable acceptance 或 exactly-once 承诺；进程在记录前崩溃时可能没有事件。不要为了掩盖这个边界重新加回 started/replay 状态机。

### 9.8 下游结果：走现有节点 output，不新增文件

实现已固定为保持业务对象字段的输出合同，仅影响声明 `tools` 的新节点：

```json
{
  "summary": "Checks are red",
  "tool_calls": [
    {"tool_name":"lookup","call_id":"engine-uuid","provider_call_id":"call-1","status":"completed","input":{"item_id":7},"output":{"checks_green":false}}
  ]
}
```

- Agent 的 `output_format.type: object` 时保留原业务字段，Engine 添加保留字段 `tool_calls`；下游读 `$inspect.output.summary` 和 `$inspect.output.tool_calls`，metrics、returns outcome/asks 等现有顶层消费者不需要迁移。
- 无 Schema、标量或数组输出使用 `{result, tool_calls}`；没有工具调用时为 `[]`。不新增输出模式配置。
- `output_format` 仍只校验模型原结果；Engine 的 `tool_calls` 来自 handler，不接受模型提交的同名字段。对象 Schema 定义该保留字段会在载入和 dispatch 时拒绝。
- 每个调用都有 Engine `call_id`；Provider 有原始 ID 时追加 `provider_call_id`（Claude 还带 MCP scope），绝不把随机 UUID 冒充 Provider ID。
- 当次调用按启动次序收集，不扫描旧 attempt，不新增 TOOL_CALLS_FILE；同步 declaredOutputPaths、类型生成、persist/hydrate 和 builder open/save，保留无工具节点原行为。
- 维护者允许输出形状由我们选择；本次选择保留顶层业务对象，是为避免打断 metrics 和 returns。无需新增运行底座或确认环节。

### 9.9 Retry 与崩溃边界

- 删除 completed receipt replay、replayOnly 和 artifact 历史扫描；正常 retried attempt 按 Agent 现有规则从头开始调用。
- 单个 attempt 内仍遵守 Provider 自有调用/响应关联，不能跨 turn 回应别人的 call ID；这与跨 attempt 重放无关。
- 未知写入使节点 non-retryable，正常失败的普通工具只回传错误。
- 不声称进程崩溃或断电后的外部副作用 exactly-once；`writes: true` 不是外部事务证明。恢复实际写业务时需要已有业务幂等/查询结果能力，不在这个首版发明通用事务日志。

### 9.10 实现范围与顺序

| 顺序 | 改动点 | 交付验证 |
|---|---|---|
| 1 | 工具声明、writes 默认值、输入 JSON Schema、Node normalize、能力预检。 | 合法声明与复杂属性可加载；未知 Provider 在模型前拒绝。 |
| 2 | NativeTool 共同合同、legacy chat 输入兼容、Claude/Codex/Pi 转换、plugin wire、catalog fingerprint。 | 每个 Provider 与插件 round-trip 传递相同复杂参数和调用 ID。 |
| 3 | script node 与工具共享执行，删除独立 refusal/replay/digest 机制。 | 工具与普通 script 在相同环境/超时/隔离下行为一致。 |
| 4 | 普通 tool error、unknown write non-retryability、一条调用事件。 | failed read 不失败节点；中断 write 停止节点且不可重试；事件含真实输入输出。 |
| 5 | Agent output envelope、字段解析、类型生成、persist/hydrate、删除 TOOL_CALLS_FILE。 | 后续节点、冷恢复、child 均可沿 `$node.output` 读取。 |
| 6 | 文档、聚焦测试、现有回归、CI static、生成检查。 | 不声明工具的 chat/Workflow、script 原行为不变。 |
| 7 | 真实模型端到端验证，审查最终 diff，创建精简 PR。 | 提供真实 call ID、调用事件、下游消费和运行结果；明确实际费用/用量。 |

可迁移的是原设计的核心和已验证 Provider 通道，不是把重版 37 文件的 diff 整体 cherry-pick。只搬 required seams，把通用 script 能力留给原 owner。

### 9.11 最小验收与规模目标

必须覆盖维护者要求的五类核心验收，以及它们直接关联的边界：

1. Codex、Claude、Pi 各有真实 native adapter 调用测试，complex JSON 参数不被降成字符串，plugin wire 不丢调用 ID。
2. 数字、array、nested object 正例，以及非法 required/type/schema 负例；非法输入启动次数为零。
3. failed read 返回工具错误，Agent 收到反馈后仍可输出结果；正常业务拒绝不导致 node_failed。
4. `writes: true` 超时/取消/断连结果不确定时仅执行一次、node retryable=false、不会启动后续写；保留 Provider 原始失败原因。
5. 每调用一事件且输入/输出正确；下游节点读到 Engine 输出，冷恢复与声明字段校验一致。
6. 正常 retry 从头开始、不重放前次工具结果；无 tools 的既有节点结果不变。
7. 普通 script 支持的 host/container 路径保持一致；不通过新 refusal 把缺口藏起来，也不冒称未验证的容器取消保证。
8. 一次真实模型 E2E 用临时项目和本地模拟业务脚本，调用只读 scratch 业务脚本，再由后续节点读取结果；未知写入用确定性测试覆盖，避免无必要的真实写入；不碰生产仓库/Issue，不把 mock server 当真实模型。

体量目标是相对最新 `dev` 的精简 diff，明显低于完整版本的一半。按当前 2163 行新增粗略量化为低于约 1000 行新增，包括必要测试；不是删除验收、安全和生成文件来凑数字。超出时先检查重复脚本内核、独立输出通道和不必要状态，而不是继续加 abstraction。

### 9.12 开工前固定的两项合同

1. 对象 Agent 结果保留顶层业务字段并追加 tool_calls；其余结果使用 result + tool_calls。已按 9.8 固定，模型校验和无工具节点输出不变。
2. `writes` 仅决定未知执行结果的重试治理，不授予权限，也不证明外部事务结果。以实际 subprocess/Provider 结构化事实区分已观察失败与未知写入，不按自然语言猜测。

其他内容可以按第 9 节执行，不再重新讨论完整 harness 定位、重新开候选 Issue 或新增知识库文件。

### 9.13 架构指导来源

本次按 `agents-best-practices` 进行工具风险、验证、重试和记录边界检查。安装 checkout 与 canonical main 均为 `da245f8cbfc4c358e8c3cde61dbb703bd40292bc`，version `1.18.0`；已做 upstream freshness 核对，无需更新安装目录。仅引用其与当前工具设计直接相关的内容，不把 MVP blueprint、always-on、自进化等机制引入本 PR。





## 10. 精简版落地与验证（2026-11-19）

- 实施对象是 Archon 的 Engine + Provider 边界，不修改 codexwright，不写 knowledge-base。原 #5897 完整分支和 a35802f8c 保留，精简分支为 codex/issue-5230-script-tools-lite。
- 工具复用普通 script 的发现、执行、凭证脱敏、冻结源码读检查、隔离环境和输出认证。保留普通 script 本来就有的源码完整性机制，不新增 tool receipt digest 或 downstream 复核。
- 参数 JSON Schema 由 Engine 的 AJV 权威校验；Provider 的 JSON Schema 输入通道只承载原始数据和工具声明，不经 Zod 反向转换改变 default/整数/嵌套语义。原 chat 工具 schema 仍按旧通道验证。
- 只保留 attempt 内 pending writes 及 unknown-write 标记；普通失败反馈给 Agent，未知写入强制 non-retryable；Provider 失败原因和数据持久化失败不被替换为成功。
- 无 replay、digest、tool artifact 输出协议、独立 container refusal、通用 latch/drain 框架。
- 真实模型：2026-11-19 00:25 上海时间，CLI + file store + Codex app-server + catpaw-cli/kimi-k3.1-pro 完整运行成功。Run ID 1050e343-9a73-4cf9-8284-bd5915a5a568，Provider call ID lookup_0_42d4c144，输入 count=2.5/items=[{id:7}]，工具返回 green=false/item_id=7，后续 consume script 从 INPUTS_CALLS 断言同一结果并输出 verified=true。
- 真实记录 token：input=18576/output=264；费用未报告，不能写成免费或零费用。使用现有本机 Codex 配置，不声称这是 OpenAI GPT 模型，也不声称 Claude/Pi 已真实模型端到端验收。
- 证据保留于 /tmp/archon-tools-lite-live-20261119/，完整静态日志 /tmp/archon-tools-lite-static.log；测试使用 Bun 1.4.2 和 package runner，无数据库结构变化。
- 远端交付已验证：新 PR #5951（https://github.com/coleam00/Archon/pull/5951），head 0ce4a552d；原 Issue #5230 新评论 6985104453，既有实施评论 6945571363 已更新；旧 PR #5897 新评论 6985113311 @Wirasm 并链接新 PR，旧 PR 已关闭为 superseded，旧分支不删除。

### 最终验收

- 最终精简 diff：39 文件，1056 新增/109 删除；旧版 2163 新增/56 删除，新增下降约 51%。新增量含 Provider/Engine 测试和生成合同；核心 runtime 185 行，不声称文件数也减半。
- 最终完整 Providers package：1534 pass / 0 fail，74 隔离分组；早先一次 Pi 本地 stub 404 的 selector 独立重跑和全量最终重跑均通过，无无关修复。
- Provider-contract 263 pass；工具核心 11 pass；Agent 70/script 42/pack 3/structured-output 24 的定向回归通过；builder round-trip 20 pass。全仓 static Validate 和 ratchet 通过，无 waiver。
- 最终 head 的第二次真实模型运行：8c698663-3ba9-45be-a6d3-355d58d9864b；Engine call e2540ab3-48cc-4a3d-84e1-39c246efa60d，Provider call lookup_0_07196558，输入/输出/后续断言与前次相同。Token input=18580/output=223，费用仍未知。原始文件 /tmp/archon-tools-lite-live-20261119/live-final-output.log。
- 待维护者 review/merge；当前远端 PR 可合并但不等于已通过远端 CI 或已发布。未运行 live Claude/Pi、Docker 和 Windows，不声称其端到端验证完毕。


## 11. 维护者终审后的精简迭代（2026-11-19）

维护者在 #5951 的最新意见撤销了此前“下游读取 tool_calls”的要求。最终合同是 Agent 在自己的 turn 中取得工具结果并生成普通 output，Engine 只额外保存 script_tool_call 事件。实现仍在原 PR，不新开分支或 PR。

- 删除 schemas/tool-output.ts、输出包装、保留字段检查和派生 output paths/types；builder 仅保留 tools 声明 open/save 所必需的 key 和 round-trip，避免声明被静默丢弃。
- 工具 JSON 参数改走 named-script invocation 的 stdin，不再使用 ARCHON_TOOL_INPUT；140 KiB 输入有真实脚本回归。
- Provider JSON Schema 使用只读校验：非法 required/type/additionalProperties 被拒绝，原始输入不经 default 或 Zod 转换后交给 Engine；三家 native adapter 与 plugin wire 均有覆盖。
- providerNotCalled 按 workload 是否开始记录；quiet unknown-write 不再被标成用户取消；写调用停止最多等待 1 秒，未结束的写只记录一次 unknown 且节点 non-retryable，迟到结果不重复记录。
- Windows owned-group abort 不再依赖 recorder。上游拆分 subprocess-tree.test.ts 后，回归测试随新文件保留。
- loop CI 失败仅为 SAMPLE_AI_FIELD_VALUES 缺少 tools 示例，补 fixture 后 70 项通过；未扩展 loop 的工具能力。
- 文档恢复 Bash and script node timeouts 为三级标题，并改为 stdin 和普通 Agent output 的说明。

最终功能提交 e3907cb5e，合并当前 dev 后 head f173388b8642fef4fd67636034565caf7f89e281，已 push 到 PR #5951。PR 正文、PR 评论 6992918760 和原 Issue 评论 6992925091 已更新，明确撤回旧下游输出方案。

验证：工具核心 14 pass，loop 70 pass，Provider contract 263 pass，Provider 全量 1534 pass / 0 fail，builder 20 pass，合并后 static 与 ratchet 通过。Workflows 全量 3683 pass 后仅有两条 uv 0.9.21 警告断言失败，未修改基线同样失败；合并后 package-tests 的两条 Git safe-directory 失败也在未修改基线复现，均不作为本 PR 修复范围，不修改无关测试掩盖。

真实模型：run 3511fca6-b861-465b-80b3-bb825c0aff2d，Codex app-server 0.167.0 + catpaw-cli/kimi-k3.1-pro，lookup 从 stdin 读取 count=2.5/items=[{id:7}]，Provider call lookup_0_72bb7302，只写一条 completed 事件。节点 structured_output 恰为 {summary:'Checks are red',green:false}，declared_fields 只有 summary/green。Token input=18529/output=138，费用未报告。证据 /tmp/archon-tools-followup-live-20261119/。

远端 Docs Build 和 Test Suite 当前为 action_required，等待维护者批准 fork CI；这与 CI 通过、维护者接受或合并不同，不能提前宣称完成。未运行 live Claude/Pi、Docker 或本机 Windows；Windows 用例交给远端 Windows CI。
