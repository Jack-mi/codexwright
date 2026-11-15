import asyncio
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from codexwright.contracts import ArchitectureSpec
from codexwright.target import scaffold
from test_generated_workflow import FakeCodex, FakeThread, load


def generated(tmp_path, spec_dict, monkeypatch, codex=FakeCodex):
    root = tmp_path / "generated"
    root.mkdir()
    scaffold(root, ArchitectureSpec.model_validate(spec_dict))
    module = load(root)
    monkeypatch.setattr(module, "AsyncCodex", codex)
    return module


def iterative_spec(spec_dict):
    data = copy.deepcopy(spec_dict)
    data["orchestration"].update(
        mode="iterative",
        max_iterations=2,
        stop_when={"packet": "normalize", "field": "value", "equals": "OK"},
    )
    return data


def sequence_codex(responses):
    values = iter(responses)

    class SequenceThread(FakeThread):
        async def turn(self, value, **kwargs):
            response = next(values)

            class Handle:
                id = "turn-sequence"

                async def run(self):
                    return SimpleNamespace(id=self.id, status="completed", error=None, final_response=json.dumps({"value": response}), usage=None, items=[])

                async def interrupt(self):
                    pass

            return Handle()

    class SequenceCodex(FakeCodex):
        async def thread_start(self, **kwargs):
            return SequenceThread("sequence-thread")

    return SequenceCodex


def test_iterative_workflow_reaches_bounded_stop_condition(tmp_path, spec_dict, monkeypatch):
    module = generated(tmp_path, iterative_spec(spec_dict), monkeypatch, sequence_codex(["NO", "OK"]))
    result = asyncio.run(module.run({"value": "hello"}))
    assert result["status"] == "passed"
    assert result["iteration"] == 2
    assert result["output"] == {"value": "OK"}
    assert [item["stop_condition_met"] for item in result["iterations"]] == [False, True]
    assert result["previous_outputs"] == {"normalize": {"value": "NO"}}


def test_iterative_workflow_fails_instead_of_claiming_success_at_limit(tmp_path, spec_dict, monkeypatch):
    module = generated(tmp_path, iterative_spec(spec_dict), monkeypatch, sequence_codex(["NO", "NO"]))
    result = asyncio.run(module.run({"value": "hello"}))
    assert result["status"] == "failed"
    assert result["iteration"] == 2


def test_iterative_manual_compaction_requires_public_completion_evidence(tmp_path, spec_dict, monkeypatch):
    data = iterative_spec(spec_dict)
    data["agents"][0]["compact_between_iterations"] = True

    class CompactingThread(FakeThread):
        responses = iter(["NO", "OK"])

        def __init__(self, name):
            super().__init__(name)
            self.compacted = False

        async def turn(self, value, **kwargs):
            response = next(self.responses)

            class Handle:
                id = "turn-sequence"

                async def run(self):
                    return SimpleNamespace(id=self.id, status="completed", error=None, final_response=json.dumps({"value": response}), usage=None, items=[])

                async def interrupt(self):
                    pass

            return Handle()

        async def compact(self):
            self.compacted = True

        async def read(self, *, include_turns=False):
            turns = []
            if self.compacted:
                turns = [SimpleNamespace(id="compaction-turn", status="completed", error=None, items=[{"id": "compaction-item", "type": "contextCompaction", "completedAtMs": 1}])]
            return SimpleNamespace(thread=SimpleNamespace(turns=turns))

    class CompactingCodex(FakeCodex):
        async def thread_start(self, **kwargs):
            return CompactingThread("compacting-thread")

    module = generated(tmp_path, data, monkeypatch, CompactingCodex)
    result = asyncio.run(module.run({"value": "hello"}))
    assert result["status"] == "passed"
    assert result["context_compactions"] == [{"iteration": 1, "agent": "worker", "turn_id": "compaction-turn", "item_id": "compaction-item", "status": "completed"}]
    assert result["compaction_usage_unmeasured"] is True


def test_unconfirmed_compaction_is_reconciled_without_restarting_it(tmp_path, spec_dict, monkeypatch):
    data = iterative_spec(spec_dict)
    data["agents"][0].update(compact_between_iterations=True, timeout_seconds=1)

    class SlowCompactionThread(FakeThread):
        responses = iter(["NO", "OK"])

        def __init__(self, name):
            super().__init__(name)
            self.compact_calls = 0
            self.allow_completion = False

        async def turn(self, value, **kwargs):
            response = next(self.responses)

            class Handle:
                id = "turn-sequence"

                async def run(self):
                    return SimpleNamespace(id=self.id, status="completed", error=None, final_response=json.dumps({"value": response}), usage=None, items=[])

                async def interrupt(self):
                    pass

            return Handle()

        async def compact(self):
            self.compact_calls += 1

        async def read(self, *, include_turns=False):
            turns = []
            if self.allow_completion:
                turns = [SimpleNamespace(id="compaction-turn", status="completed", error=None, items=[{"id": "compaction-item", "type": "contextCompaction", "completedAtMs": 1}])]
            return SimpleNamespace(thread=SimpleNamespace(turns=turns))

    thread = SlowCompactionThread("slow-compaction")

    class SlowCompactionCodex(FakeCodex):
        async def thread_start(self, **kwargs):
            return thread

        async def thread_resume(self, thread_id, **kwargs):
            return thread

    module = generated(tmp_path, data, monkeypatch, SlowCompactionCodex)
    checkpoint = tmp_path / "checkpoint.json"
    with pytest.raises(RuntimeError, match="Compaction completion unknown"):
        asyncio.run(module.run({"value": "hello"}, state_path=checkpoint))
    with pytest.raises(RuntimeError, match="reconcile it before resuming"):
        asyncio.run(module.run({"value": "hello"}, state_path=checkpoint))
    thread.allow_completion = True
    result = asyncio.run(module.run({"value": "hello"}, state_path=checkpoint, recover=True))
    assert result["status"] == "passed"
    assert thread.compact_calls == 1
    assert [item["iteration"] for item in result["iterations"]] == [1, 2]


def test_recovery_reconciles_read_only_turn_before_retry(tmp_path, spec, monkeypatch):
    module = generated(tmp_path, spec, monkeypatch)
    request = {"value": "hello"}
    identity = hashlib.sha256(json.dumps({"spec": module.SPEC, "input": request}, sort_keys=True).encode()).hexdigest()
    checkpoint = tmp_path / "checkpoint.json"
    checkpoint.write_text(json.dumps({
        "identity": identity,
        "request": request,
        "status": "running",
        "threads": {"worker": "saved-thread"},
        "tokens": 0,
        "turns": 0,
        "packets": {"normalize": {"status": "outcome_unknown", "thread_id": "saved-thread", "turn_id": "saved-turn"}},
    }))

    class RecoveredThread(FakeThread):
        async def read(self, *, include_turns=False):
            return SimpleNamespace(thread=SimpleNamespace(turns=[SimpleNamespace(id="saved-turn", status="completed")]))

    async def resume(self, thread_id, **kwargs):
        return RecoveredThread(thread_id)

    monkeypatch.setattr(FakeCodex, "thread_resume", resume)
    result = asyncio.run(module.run(request, state_path=checkpoint, recover=True))
    assert result["status"] == "passed"
    assert result["output"] == {"value": "OK"}
    assert result["recovery_usage_unmeasured"] is True
    assert result["packets"]["normalize"]["usage_unmeasured"] is True


def test_recovery_does_not_replay_unknown_writes(tmp_path, spec_dict, monkeypatch):
    data = copy.deepcopy(spec_dict)
    data["agents"][0]["sandbox"] = "workspace_write"
    module = generated(tmp_path, data, monkeypatch)
    request = {"value": "hello"}
    identity = hashlib.sha256(json.dumps({"spec": module.SPEC, "input": request}, sort_keys=True).encode()).hexdigest()
    checkpoint = tmp_path / "checkpoint.json"
    checkpoint.write_text(json.dumps({
        "identity": identity,
        "request": request,
        "status": "running",
        "threads": {},
        "tokens": 0,
        "turns": 0,
        "packets": {"normalize": {"status": "outcome_unknown", "thread_id": "saved-thread", "turn_id": "saved-turn"}},
    }))
    with pytest.raises(RuntimeError, match="still has an unknown outcome"):
        asyncio.run(module.run(request, state_path=checkpoint, approve_writes=True, recover=True))


def native_spec(spec_dict):
    data = copy.deepcopy(spec_dict)
    data["baseline"] = {"single_agent_sufficient": False, "reason": "Dynamic independent exploration", "comparison": ["Native delegation avoids a fixed host topology"]}
    data["agents"].append({**data["agents"][0], "id": "explorer"})
    data["agents"][0]["id"] = "root"
    data["work_packets"][0]["agent"] = "root"
    data["orchestration"].update(strategy="native_subagents", root_agent="root", mode="parallel", max_parallel=2)
    data["controls"]["budget"]["max_parallel"] = 2
    return data


def test_native_subagents_record_collaboration_compaction_and_usage_boundary(tmp_path, spec_dict, monkeypatch):
    child_id = "child-thread"
    root_id = "root-thread"

    class NativeThread(FakeThread):
        id = root_id

        async def read(self, *, include_turns=False):
            items = [
                {"id": "spawn", "type": "collabAgentToolCall", "tool": "spawnAgent", "status": "completed", "senderThreadId": root_id, "receiverThreadIds": [child_id], "agentsStates": {child_id: {"status": "pendingInit", "message": "DO_NOT_RECORD"}}},
                {"id": "wait", "type": "collabAgentToolCall", "tool": "wait", "status": "completed", "senderThreadId": root_id, "receiverThreadIds": [child_id], "agentsStates": {child_id: {"status": "completed", "message": "DO_NOT_RECORD"}}},
                {"id": "compact", "type": "contextCompaction"},
            ]
            return SimpleNamespace(thread=SimpleNamespace(turns=[SimpleNamespace(id="turn_fixture", items=items)]))

    class NativeCodex(FakeCodex):
        async def thread_start(self, **kwargs):
            self.starts.append(kwargs)
            return NativeThread(root_id)

        async def thread_resume(self, thread_id, **kwargs):
            class ChildThread(FakeThread):
                async def read(self, *, include_turns=False):
                    return SimpleNamespace(thread=SimpleNamespace(agent_role="explorer", parent_thread_id=root_id, turns=[]))

            return ChildThread(thread_id)

    module = generated(tmp_path, native_spec(spec_dict), monkeypatch, NativeCodex)
    NativeCodex.starts = []
    result = asyncio.run(module.run({"value": "hello"}))
    assert result["status"] == "passed"
    assert result["native_threads"] == [child_id]
    assert result["native_roles"] == {child_id: "explorer"}
    assert result["native_usage_unmeasured"] is True
    assert result["context_compactions"] == [{"id": "compact"}]
    assert result["native_collaboration"][-1]["agentsStates"] == {child_id: {"status": "completed"}}
    assert "DO_NOT_RECORD" not in json.dumps(result)
    config = NativeCodex.starts[0]["config"]
    assert config["features"]["multi_agent"] is True
    assert config["agents"]["max_concurrent_threads_per_session"] == 2
    role_path = Path(config["agents"]["explorer"]["config_file"])
    assert 'name = "explorer"' in role_path.read_text()
    assert 'developer_instructions = ' in role_path.read_text()


def test_native_subagents_reject_incomplete_child_evidence(tmp_path, spec_dict, monkeypatch):
    class NativeThread(FakeThread):
        async def read(self, *, include_turns=False):
            items = [{"id": "spawn", "type": "collabAgentToolCall", "tool": "spawnAgent", "status": "completed", "receiverThreadIds": ["child"], "agentsStates": {"child": {"status": "pendingInit"}}}]
            return SimpleNamespace(thread=SimpleNamespace(turns=[SimpleNamespace(id="turn_fixture", items=items)]))

    class NativeCodex(FakeCodex):
        async def thread_start(self, **kwargs):
            return NativeThread("root")

    module = generated(tmp_path, native_spec(spec_dict), monkeypatch, NativeCodex)
    result = asyncio.run(module.run({"value": "hello"}))
    assert result["status"] == "failed"
    assert "completed child-agent evidence" in result["packets"]["normalize"]["error"]


def test_native_subagents_retry_with_validation_feedback(tmp_path, spec_dict, monkeypatch):
    data = native_spec(spec_dict)
    data["work_packets"][0]["retries"] = 1
    root_id = "root-thread"

    class NativeThread(FakeThread):
        reads = 0

        async def read(self, *, include_turns=False):
            self.reads += 1
            items = []
            if self.reads > 1:
                items = [{"id": "wait", "type": "collabAgentToolCall", "tool": "wait", "status": "completed", "receiverThreadIds": ["child"], "agentsStates": {"child": {"status": "completed"}}}]
            return SimpleNamespace(thread=SimpleNamespace(turns=[SimpleNamespace(id="turn_fixture", items=items)]))

    class NativeCodex(FakeCodex):
        async def thread_start(self, **kwargs):
            return NativeThread(root_id)

        async def thread_resume(self, thread_id, **kwargs):
            class ChildThread(FakeThread):
                async def read(self, *, include_turns=False):
                    return SimpleNamespace(thread=SimpleNamespace(agent_role="explorer", parent_thread_id=root_id, turns=[]))

            return ChildThread(thread_id)

    module = generated(tmp_path, data, monkeypatch, NativeCodex)
    result = asyncio.run(module.run({"value": "hello"}))
    assert result["status"] == "passed"
    assert result["packets"]["normalize"]["attempts"] == 2


def test_native_subagents_reject_undeclared_child_role(tmp_path, spec_dict, monkeypatch):
    root_id = "root-thread"

    class NativeThread(FakeThread):
        async def read(self, *, include_turns=False):
            items = [{"id": "wait", "type": "collabAgentToolCall", "tool": "wait", "status": "completed", "receiverThreadIds": ["child"], "agentsStates": {"child": {"status": "completed"}}}]
            return SimpleNamespace(thread=SimpleNamespace(turns=[SimpleNamespace(id="turn_fixture", items=items)]))

    class NativeCodex(FakeCodex):
        async def thread_start(self, **kwargs):
            return NativeThread(root_id)

        async def thread_resume(self, thread_id, **kwargs):
            class ChildThread(FakeThread):
                async def read(self, *, include_turns=False):
                    return SimpleNamespace(thread=SimpleNamespace(agent_role="untrusted-role", parent_thread_id=root_id, turns=[]))

            return ChildThread(thread_id)

    module = generated(tmp_path, native_spec(spec_dict), monkeypatch, NativeCodex)
    result = asyncio.run(module.run({"value": "hello"}))
    assert result["status"] == "failed"
    assert "undeclared role" in result["packets"]["normalize"]["error"]


def test_native_subagents_last_child_state_must_remain_completed(tmp_path, spec_dict, monkeypatch):
    root_id = "root-thread"

    class NativeThread(FakeThread):
        async def read(self, *, include_turns=False):
            items = [
                {"id": "wait-1", "type": "collabAgentToolCall", "tool": "wait", "status": "completed", "receiverThreadIds": ["child"], "agentsStates": {"child": {"status": "completed"}}},
                {"id": "wait-2", "type": "collabAgentToolCall", "tool": "wait", "status": "completed", "receiverThreadIds": ["child"], "agentsStates": {"child": {"status": "errored"}}},
            ]
            return SimpleNamespace(thread=SimpleNamespace(turns=[SimpleNamespace(id="turn_fixture", items=items)]))

    class NativeCodex(FakeCodex):
        async def thread_start(self, **kwargs):
            return NativeThread(root_id)

    module = generated(tmp_path, native_spec(spec_dict), monkeypatch, NativeCodex)
    result = asyncio.run(module.run({"value": "hello"}))
    assert result["status"] == "failed"
    assert "completed child-agent evidence" in result["packets"]["normalize"]["error"]


def test_native_recovery_checks_descendants_before_starting_a_new_tree(tmp_path, spec_dict, monkeypatch):
    data = native_spec(spec_dict)
    module = generated(tmp_path, data, monkeypatch)
    request = {"value": "hello"}
    identity = hashlib.sha256(json.dumps({"spec": module.SPEC, "input": request}, sort_keys=True).encode()).hexdigest()
    checkpoint = tmp_path / "checkpoint.json"
    checkpoint.write_text(json.dumps({
        "identity": identity,
        "request": request,
        "status": "running",
        "threads": {"root": "old-root"},
        "tokens": 0,
        "turns": 0,
        "packets": {"normalize": {"status": "outcome_unknown", "thread_id": "old-root", "turn_id": "saved-turn"}},
    }))
    FakeCodex.starts = []

    class RootThread(FakeThread):
        async def read(self, *, include_turns=False):
            items = [{"type": "collabAgentToolCall", "receiverThreadIds": ["child"], "agentsStates": {"child": {"status": "completed"}}}]
            return SimpleNamespace(thread=SimpleNamespace(turns=[SimpleNamespace(id="saved-turn", status="completed", items=items)]))

    class ChildThread(FakeThread):
        async def read(self, *, include_turns=False):
            return SimpleNamespace(thread=SimpleNamespace(turns=[SimpleNamespace(id="child-turn", status="inProgress")]))

    async def resume(self, thread_id, **kwargs):
        return RootThread(thread_id) if thread_id == "old-root" else ChildThread(thread_id)

    monkeypatch.setattr(FakeCodex, "thread_resume", resume)
    with pytest.raises(RuntimeError, match="still has an unknown outcome"):
        asyncio.run(module.run(request, state_path=checkpoint, recover=True))
    assert FakeCodex.starts == []


def test_write_packet_validation_failure_never_retries_side_effects(tmp_path, spec_dict, monkeypatch):
    data = copy.deepcopy(spec_dict)
    data["agents"][0]["sandbox"] = "workspace_write"
    data["work_packets"][0].update(retries=2, assertions=[{"field": "value", "operator": "equals", "value": "NOT OK"}])
    module = generated(tmp_path, data, monkeypatch)
    result = asyncio.run(module.run({"value": "hello"}, approve_writes=True))
    assert result["status"] == "failed"
    assert result["packets"]["normalize"]["status"] == "outcome_unknown"
    assert result["turns"] == 1
    assert "duplicate side effects" in result["packets"]["normalize"]["error"]
    checkpoint = tmp_path / "checkpoint.json"
    result = asyncio.run(module.run({"value": "hello"}, state_path=checkpoint, approve_writes=True))
    with pytest.raises(RuntimeError, match="unknown outcome"):
        asyncio.run(module.run({"value": "hello"}, state_path=checkpoint, approve_writes=True))


def test_skill_requires_executable_behavior_assertion(spec_dict):
    data = copy.deepcopy(spec_dict)
    data["skills"] = [{"name": "label", "trigger": "Format labels", "procedure": "Return a label", "references": [], "scripts": [], "eval_cases": ["hello"], "lifecycle": "generated"}]
    data["agents"][0]["skills"] = ["label"]
    with pytest.raises(ValueError, match="executable behavioral assertions"):
        ArchitectureSpec.model_validate(data)


def test_native_tool_receipts_include_child_threads(tmp_path, spec_dict, monkeypatch):
    data = native_spec(spec_dict)
    data["tools"] = [{"name": "read_file", "kind": "builtin", "implementation": "read_file", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False}, "output_schema": {"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"], "additionalProperties": False}, "risk": "read_only", "side_effect": False, "timeout_seconds": 30, "approval": "scope", "smoke_input": {"path": "a.txt"}}]
    data["verification"]["checks"].append({"id": "read_tool", "kind": "tool_smoke", "target": "tool_server.py", "arguments": ["smoke", "read_file", '{"path":"a.txt"}'], "expected": None, "required": True, "timeout_seconds": 30})
    for agent in data["agents"]:
        agent["tools"] = ["read_file"]
    root_id = "root-thread"

    class NativeThread(FakeThread):
        async def read(self, *, include_turns=False):
            items = [{"id": "wait", "type": "collabAgentToolCall", "tool": "wait", "status": "completed", "receiverThreadIds": ["child"], "agentsStates": {"child": {"status": "completed"}}}]
            return SimpleNamespace(thread=SimpleNamespace(turns=[SimpleNamespace(id="turn_fixture", items=items)]))

    class Result:
        def model_dump(self, **_kwargs):
            return {"structured_content": {"content": "alpha"}}

    tool_call = SimpleNamespace(id="call-1", type="mcpToolCall", server="workflow_tools", tool="read_file", status="completed", error=None, result=Result())

    class NativeCodex(FakeCodex):
        async def thread_start(self, **kwargs):
            return NativeThread(root_id)

        async def thread_resume(self, thread_id, **kwargs):
            class ChildThread(FakeThread):
                async def read(self, *, include_turns=False):
                    return SimpleNamespace(thread=SimpleNamespace(agent_role="explorer", parent_thread_id=root_id, turns=[SimpleNamespace(items=[tool_call])]))

            return ChildThread(thread_id)

    module = generated(tmp_path, data, monkeypatch, NativeCodex)
    result = asyncio.run(module.run({"value": "hello"}))
    assert result["status"] == "passed"
    assert result["packets"]["normalize"]["tools"] == [{"name": "read_file", "transport": "mcp_registry", "exit_code": 0, "output": {"content": "alpha"}, "call_id": "call-1"}]


def test_iteration_compaction_is_tracked_per_agent(tmp_path, spec_dict, monkeypatch):
    data = iterative_spec(spec_dict)
    data["baseline"] = {"single_agent_sufficient": False, "reason": "Independent branches", "comparison": ["Parallel independent work"]}
    data["agents"] += [{**data["agents"][0], "id": "other", "compact_between_iterations": True}, {**data["agents"][0], "id": "join", "compact_between_iterations": False}]
    data["agents"][0]["compact_between_iterations"] = True
    data["work_packets"] += [{**data["work_packets"][0], "id": "branch", "agent": "other"}, {**data["work_packets"][0], "id": "join", "agent": "join", "depends_on": ["normalize", "branch"]}]
    data["orchestration"].update(mode="iterative", max_parallel=2, result_packets=["join"], stop_when={"packet": "join", "field": "value", "equals": "OK"})
    data["controls"]["budget"]["max_parallel"] = 2

    class CompactingThread(FakeThread):
        def __init__(self, name, join=False):
            super().__init__(name)
            self.responses = iter(["READY", "NO", "READY", "OK"] if join else ["NO", "OK"])
            self.compacted = False

        async def turn(self, value, **kwargs):
            response = next(self.responses)

            class Handle:
                id = "turn-" + self.id

                async def run(self):
                    return SimpleNamespace(id=self.id, status="completed", error=None, final_response=json.dumps({"value": response}), usage=None, items=[])

                async def interrupt(self):
                    pass

            return Handle()

        async def compact(self):
            self.compacted = True

        async def read(self, *, include_turns=False):
            turns = []
            if self.compacted:
                turns = [SimpleNamespace(id="compaction-" + self.id, status="completed", error=None, items=[{"id": "compaction-item", "type": "contextCompaction", "completedAtMs": 1}])]
            return SimpleNamespace(thread=SimpleNamespace(turns=turns))

    class CompactingCodex(FakeCodex):
        async def thread_start(self, **kwargs):
            self.starts.append(kwargs)
            return CompactingThread("thread-" + str(len(self.starts)), join=len(self.starts) == 3)

    module = generated(tmp_path, data, monkeypatch, CompactingCodex)
    CompactingCodex.starts = []
    result = asyncio.run(module.run({"value": "hello"}))
    assert result["status"] == "passed", result["packets"]
    assert {item["agent"] for item in result["context_compactions"]} == {"worker", "other"}
    assert result["last_compaction_iterations"] == {"worker": 1, "other": 1}
