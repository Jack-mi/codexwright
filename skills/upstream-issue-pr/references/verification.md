# 验证与状态清单

只在实现、review 或更新 PR 需要时读取本清单。按 issue 选择相关项，不要求每个小 PR 跑完整矩阵。

## 验收证据表

为 issue 的每条公开承诺保留一行：

| Claim | 入口与场景 | 负例/攻击路径 | 断言位置 | Mutation | Head |
| --- | --- | --- | --- | --- | --- |
| 用户可见结果 | 真实 Engine 主流程 | 非法输入/漂移/旁路 | Engine 返回后的外层断言 | 删除 guard 后失败 | 精确 SHA |

先写用户旅程，再写实现细节测试。以下情况不能算主流程已验证：

- 只测了 resolver、schema 或 mock handler，没有运行实际启动路径。
- 声明支持插件或 pack，却只测 in-process 或共享脚本。
- 声明跨 run/child/resume 有效，却只测首次父 run。
- 声明 dry-run 与真实运行一致，却各自实现并各测一个分支。

## 最小完整覆盖总账

每个验收项至少核对下面各列；不适用时写明原因，不留空白。

| 验收项 | 实现 owner | 所有调用方/入口 | 正例 | 负例/旁路 | 兼容/恢复 | 文档与当前状态 |
| --- | --- | --- | --- | --- | --- | --- |
| 用户可见承诺 | 复用的共享模块 | UI/CLI/API/插件/child 等实际入口 | 主流程证据 | 拒绝、漂移、重复 occurrence | 旧行为、重试、恢复 | 精确 head 与未验证项 |

每次缩围同时问“哪条验收被删除，维护者是否同意”；每次加机制同时问“哪条验收要求它，能否复用现有 owner”。两种问题都必须有答案。

## 测试裁判检查

- 把最终断言放在被测 Engine/Provider 返回之后；回调或 generator 内异常可能被被测系统捕获。
- mock 只提供输入和记录事实，不用 mock 自己抛出的异常证明生产校验存在。
- 先记录 handler/script 是否进入，再断言参数；非法输入必须证明启动次数为零。
- 循环、fan-out、多个 wait 和多个工具调用逐个验证所有 occurrence，不能用一次匹配掩盖后续漂移。
- 比较结构化值时用深度相等和明确语义，区分 `undefined`、JSON `null`、字符串 `"null"`。
- 安全预览只投影允许展示的字段；选择后的 typed output 与未回答预览分别测试。
- 持久化审计检查独立副本的 key、字符串值和非字符串标量，脱敏冲突不得覆盖其他字段。
- 取消/超时测试先等脚本真正启动，再让 Provider 结束；断言节点没有悄悄失败。
- 对核心 guard 做最小 mutation，确认测试失败后恢复；恢复后的最终通过才算交付证据。mutation 只能由实施 Agent 在其可写范围内执行，或放在一次性 scratch copy；只读 review 不修改目标 worktree，改为检查已有 mutation 证据、使用非修改性负对照或标明缺口。
- 测试数量按 runner 的最终汇总和退出码报告，不对包含重试或多个 isolation group 的整份日志手工累加。

## Review 台账

每条人类或自动反馈保留：

| 状态 | 含义 |
| --- | --- |
| open | 尚未在当前 head 核实 |
| reproduced | 当前 head 已复现，待修 |
| fixed | 本地已改，但对应回归尚未通过 |
| verified | 当前 head 的回归和必要 mutation 已通过 |
| stale | 针对旧 head 或已被后续合同删除 |
| rejected | 核实后不成立，记录反证 |

`No actionable comments in recent review` 只说明该次增量 review，不会自动把台账里的旧 `open` 项清零。

## 状态词典

| 状态 | 可以声称什么 | 不能额外推断什么 |
| --- | --- | --- |
| committed | 本地有提交 | 已推送或已验收 |
| pushed | 远端 head 已读回一致 | review 或 CI 已覆盖该 head |
| review pending | 已请求 review | review 通过 |
| CodeRabbit SUCCESS | 当前显示该检查成功 | 人工批准、旧反馈全解决或 CI 全绿 |
| MERGEABLE | Git 当前无合并冲突 | 可合并、已通过或维护者接受设计 |
| action_required | fork workflow 等维护者批准 | CI 正在运行或测试已通过 |
| CI passed | 指定 head 的指定 jobs 通过 | live E2E、所有平台或人工批准 |
| live E2E passed | 指定 head/Provider/场景真实跑通 | 其他 head 或 Provider 同样通过 |
| merged | 已进入目标分支 | 之前每个中间方案都正确或必要 |

## 最小 PR 状态块

```text
Head: <sha>, Base: <sha>
Tree: <clean at sha | sha + uncommitted diff，附 diff digest/状态>
Changed: <当前合同和范围>
Verified on this exact tree: <命令和结果>
Not verified: <live/平台/未运行项>
Remaining issue acceptance: <尚未完成的验收；无则写 none>
External gate: <审批者需要做的唯一下一步>
```

新 head 或新的未提交 diff 产生新的状态块；旧状态标为历史。只有 `Tree` 为 clean 且与 head 一致时才能写“此 head 已验证”，否则必须保留 `HEAD + uncommitted diff` 限定。存在剩余验收时使用 `Refs`，全部完成或维护者明确删除后才使用 `Closes`。只有实质性进展才新增公开评论。
