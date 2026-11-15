# Codex Harness Capabilities

Checked 2026-11-15 against the installed public `openai-codex` 0.167.0 API,
its pinned runtime, current official Codex documentation, and scoped runtime
probes. The public Python API and the underlying harness are related but not
identical surfaces.

## Control Layers

```text
codexwright / generated workflow
  ArchitectureSpec, DAG or native strategy, budgets, validation, recovery, evidence
      -> public AsyncCodex Thread/Turn/config APIs
      -> local codex app-server JSON-RPC
      -> Codex agent loop, tools, sandbox, native collaboration and compaction
```

There is no public host `spawn_agent()` Python method. Native delegation is
started through an ordinary root Turn with supported multi-agent configuration;
the root model invokes runtime collaboration tools. Host delegation instead
calls `AsyncCodex.thread_start()` for each independent top-level Thread.

## Strategy Selection

| Strategy | Appropriate work | Current guarantees | Explicit boundary |
| --- | --- | --- | --- |
| Single Thread | Ordinary tasks and the required baseline | One role and one continuous context | No unnecessary MAS overhead |
| Host DAG | Fixed dependencies, differentiated permissions, per-packet schemas, strict recovery and audit | Host-owned concurrency, schemas, receipts, retries, budgets and terminal reconciliation | More host code; no model-driven topology |
| Native subagents | Dynamic, independent, read-only exploration | Declared roles, shared root scope, bounded concurrency, `max_depth=1`, root output validation and child terminal evidence | Child usage is unavailable through public 0.167 reads; no writes, side effects, per-role sandboxes or per-child deterministic acceptance |

Child roles are generated as private `CODEX_HOME/agents/*.toml` files with
`name`, `description`, `developer_instructions`, and optional model/effort, then
registered through `agents.<name>.config_file`. Root instructions choose which
configured role to use and when. Completion reconciliation resumes every child
and rejects an undeclared `agentRole` or incorrect `parentThreadId`. Exact spawn
order and timing remain model-executed orchestration; use host DAG when those
are hard acceptance requirements.

Native execution records `collabAgentToolCall` on pinned 0.167 and accepts the
documented `collabToolCall` shape as well. Spawn completion alone is not child
completion: `receiverThreadIds` must also have terminal `agentsStates` evidence.
The last observed state wins, so a later error or interruption cannot be hidden
by an earlier completion. Tool receipts are collected from both the root and
child Thread items rather than assuming the root invoked every tool.
Missing delegation, incomplete children, invalid roles, and root output
validation failures use the packet's bounded validation-feedback retries.
Collaboration records retain lifecycle metadata, not child messages, prompts,
reasoning, or secrets.

`native_usage_unmeasured=true` means `tokens` and `turns` describe the observed
root execution, not the whole parent/child tree. Strict whole-tree token budgets
must use host Threads or wait for a newer public descendant-usage contract.

## Iteration And Compaction

Host `iterative` mode repeats a declared DAG only when all work is read-only and
side-effect free. `max_iterations` is bounded and `stop_when` is executable;
reaching the iteration limit without the condition is failure, not success.
Previous outputs are passed as untrusted refinement evidence and retained in the
checkpoint.

`thread.compact()` acknowledges a request. It does not prove compaction finished.
Optional `compact_between_iterations` records earlier Turn IDs, starts compaction,
then performs bounded public `thread.read(include_turns=True)` reconciliation. A
new `contextCompaction` item must have `completedAtMs` in a completed, error-free
Turn. Timeout is unknown completion, not success. Manual compaction usage is
marked unmeasured; automatic compaction items are also retained when observed.

## Recovery

Generated packets persist `thread_id` and `turn_id` when a Turn starts. Ordinary
resume refuses `running` and `outcome_unknown` records. `recover` first resumes
the original Thread and reads the original Turn:

- a terminal original Turn makes a read-only packet safe to retry;
- native recovery also reads every discoverable descendant and keeps the run
  unknown if any child is active or lacks terminal evidence;
- an active or missing terminal record remains unknown;
- workspace writes and side-effect tools are never replayed automatically;
- write-packet validation failures never trigger another execution attempt;
- recovered historical usage that cannot be read back is marked
  `recovery_usage_unmeasured` instead of being omitted from the evidence;
- a passed checkpoint is revalidated, not executed again.

## Generated MCP Approval

Read-only `mas_run` and `mas_recover` execute directly. If the architecture has a
workspace-write Agent or any side-effect tool, the generated MCP requires a
host-injected trusted approval handler. The handler receives the operation,
validated run ID, spec revision and exact request SHA-256, and owns real human
confirmation. Without that handler, writes are `blocked` even if a model-driven
client can automatically answer a bare MCP form. Declined or failed confirmation
does not execute the workflow. No model-filled `approve_writes` argument is
exposed. Standalone stdio startup intentionally has no trusted handler; an
embedding host must inject one after commissioning its actual human UI.

## Capability Freshness

The project remains pinned to SDK/runtime 0.167.0; upgrading is a separate
compatibility decision. Do not infer pinned behavior from current documentation
alone. Recheck public signatures, feature flags, item discriminators, usage
scope, and compaction evidence against the installed runtime before changing the
pin.
