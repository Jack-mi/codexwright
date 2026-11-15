# Architecture decisions

The executable ArchitectureSpec and service are authoritative; this reference supplies model decision criteria.

- Establish source_runtime by real entrypoints, imports, dependencies, state, tools and handoffs. Installing a package alone does not prove it is used.
- none → new Codex SDK project; codex_sdk → reuse and local edit; other → behavior capture and rebuild; unknown → inspect and ask only a blocking question.
- Start with one role/thread. Multiple roles require independently divisible work, distinct trust/permission contexts, or useful independent verification. Store the reason and baseline comparison.
- Host Python controls the flow, permissions, validation, state, integration, budgets and stopping. The model analyzes, generates code and diagnoses semantics.
- `host_dag` remains the default execution strategy. `native_subagents` is for dynamic read-only exploration only: one root result packet, declared child roles, shared root tool/Skill scope, bounded concurrency and `agents.max_depth=1`. Public SDK 0.167 does not expose descendant usage, so native runs record `native_usage_unmeasured` and are not suitable for strict whole-tree token budgets or per-child deterministic acceptance.
- Host `iterative` mode is bounded by `max_iterations` and an executable `stop_when`; repeated work must be read-only and side-effect free. Manual compaction requires public completion evidence from a bounded `thread.read()` reconciliation, not just `thread.compact()` acknowledgement.
- Generated checkpoints retain Thread/Turn IDs. Recovery reconciles the original terminal turn before retrying read-only packets; unknown writes remain `outcome_unknown`.
- Skill is reusable procedural knowledge; deterministic repeated operations become scripts; tools provide narrow current data/actions. Do not generate Skills for one-off task prose.
- The target is a standalone package using public openai_codex exports. Default service forms are library, CLI and stdio MCP. HTTP, plugins and resident workers are optional deliverables when requested.
- Build/edit/migrate/refactor prepare exact file proposals in isolation. User authorization binds proposal hash, spec revision and workspace snapshot. Only apply writes the target.
- Preserve failure and incomplete coverage. Deterministic command receipts and artifacts establish runnable behavior; model verdicts are supplementary.
- Migration parity requires golden inputs/outputs plus errors, permissions, side effects and recovery criteria. Old runtime imports/entrypoints/unused dependencies must be retired only within approved scope. An unexecutable old system is a rebuild with limited evidence, not proven parity.

Architecture sources checked 2026-11-15: agents-best-practices 1.18.0 at da245f8cbfc4c358e8c3cde61dbb703bd40292bc; official Codex SDK documentation and installed public signatures; published SDK/runtime 0.167.0. The 2026-11-08 source review remains in `docs/project-evaluations.md`.
