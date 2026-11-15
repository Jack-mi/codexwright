import asyncio
from types import SimpleNamespace

from codexwright.runtime import CodexRuntime, sdk_capabilities


class RawNotification:
    def __init__(self, params):
        self.params = params

    def model_dump(self, **_kwargs):
        return {"params": self.params}


def event(method, params):
    return SimpleNamespace(method=method, payload=RawNotification(params))


def completed_turn():
    return SimpleNamespace(
        method="turn/completed",
        payload=SimpleNamespace(turn=SimpleNamespace(status="completed", error=None, duration_ms=1)),
    )


def test_native_collaboration_and_compaction_metadata_is_private(tmp_path):
    events = []
    runtime = CodexRuntime(tmp_path, event=lambda kind, **fields: events.append((kind, fields)))
    runtime.handle_threads["turn-parent"] = "thread-parent"

    class Handle:
        id = "turn-parent"

        async def stream(self):
            yield event("item/started", {
                "threadId": "thread-parent", "turnId": "turn-parent",
                "item": {
                    "id": "collab-1", "type": "collabAgentToolCall", "tool": "spawnAgent",
                    "status": "inProgress", "senderThreadId": "thread-parent",
                    "newThreadId": "thread-child", "receiverThreadIds": [], "agentsStates": {}, "prompt": "SECRET PROMPT",
                    "reasoning": "PRIVATE REASONING", "agentStatus": "inProgress",
                },
            })
            yield event("item/completed", {
                "threadId": "thread-parent", "turnId": "turn-parent",
                "item": {
                    "id": "collab-1", "type": "collabAgentToolCall", "tool": "spawnAgent",
                    "status": "completed", "senderThreadId": "thread-parent",
                    "receiverThreadIds": ["thread-child"], "newThreadId": "thread-child",
                    "agentsStates": {"thread-child": {"status": "completed", "message": "SECRET RESULT"}},
                    "prompt": "SECRET PROMPT",
                },
            })
            yield event("item/started", {
                "threadId": "thread-parent", "turnId": "turn-parent",
                "item": {"id": "compact-1", "type": "contextCompaction", "summary": "SECRET SUMMARY"},
            })
            yield event("item/completed", {
                "threadId": "thread-parent", "turnId": "turn-parent",
                "item": {"id": "compact-1", "type": "contextCompaction", "summary": "SECRET SUMMARY"},
            })
            yield SimpleNamespace(
                method="thread/tokenUsage/updated",
                payload=SimpleNamespace(
                    thread_id="thread-parent", turn_id="turn-parent",
                    token_usage={"total": {"totalTokens": 120}, "last": {"totalTokens": 120}},
                ),
            )
            yield completed_turn()

    result = asyncio.run(runtime.collect(Handle()))
    native = [fields for kind, fields in events if kind == "runtime_event" and fields.get("item_type") in {"collabAgentToolCall", "contextCompaction"}]
    assert [(item["item_type"], item["method"], item["status"]) for item in native] == [
        ("collabAgentToolCall", "item/started", "inProgress"),
        ("collabAgentToolCall", "item/completed", "completed"),
        ("contextCompaction", "item/started", "inProgress"),
        ("contextCompaction", "item/completed", "completed"),
    ]
    assert all(item["thread_id"] == "thread-parent" and item["turn_id"] == "turn-parent" for item in native)
    assert native[0]["parent_thread_id"] == "thread-parent"
    assert native[0]["child_thread_id"] == native[0]["new_thread_id"] == "thread-child"
    assert native[0]["tool"] == "spawnAgent"
    assert native[1]["receiver_thread_ids"] == ["thread-child"]
    assert native[1]["child_thread_ids"] == ["thread-child"]
    assert native[1]["agent_statuses"] == {"thread-child": "completed"}
    assert all(item["item_id"] for item in native)
    assert "SECRET" not in repr(events) and "PRIVATE" not in repr(events)
    assert result.status == "completed"
    assert runtime.tokens == 120 and runtime.usage["inference_calls"] == 1


def test_documented_collaboration_item_uses_same_safe_metadata(tmp_path):
    events = []
    runtime = CodexRuntime(tmp_path, event=lambda kind, **fields: events.append((kind, fields)))

    class Handle:
        id = "turn-parent"

        async def stream(self):
            yield event("item/completed", {
                "threadId": "thread-parent", "turnId": "turn-parent",
                "item": {
                    "id": "wait-1", "type": "collabToolCall", "tool": "wait",
                    "status": "completed", "senderThreadId": "thread-parent",
                    "receiverThreadId": "thread-child", "agentStatus": "SECRET RESULT",
                    "prompt": "SECRET PROMPT",
                },
            })
            yield completed_turn()

    asyncio.run(runtime.collect(Handle()))
    fields = next(fields for kind, fields in events if kind == "runtime_event" and fields.get("item_type") == "collabToolCall")
    assert fields["tool"] == "wait"
    assert fields["parent_thread_id"] == "thread-parent"
    assert fields["child_thread_id"] == fields["receiver_thread_id"] == "thread-child"
    assert fields["new_thread_id"] is None and fields["agent_statuses"] == {}
    assert "agent_status" not in fields
    assert "SECRET" not in repr(events)


def test_typed_item_collection_and_usage_are_unchanged(tmp_path):
    events = []
    runtime = CodexRuntime(tmp_path, event=lambda kind, **fields: events.append((kind, fields)))

    class Handle:
        id = "turn-1"

        async def stream(self):
            yield SimpleNamespace(
                method="item/completed",
                payload=SimpleNamespace(item=SimpleNamespace(type="agentMessage", phase="final_answer", text="okay")),
            )
            yield SimpleNamespace(
                method="thread/tokenUsage/updated",
                payload=SimpleNamespace(thread_id="thread-1", token_usage={"total": {"totalTokens": 40}, "last": {"totalTokens": 40}}),
            )
            yield completed_turn()

    result = asyncio.run(runtime.collect(Handle()))
    assert result.final_response == "okay"
    assert runtime.tokens == 40 and runtime.usage["inference_calls"] == 1
    assert [kind for kind, fields in events].count("usage_updated") == 1


def test_capabilities_separate_host_api_from_native_harness():
    capabilities = sdk_capabilities()
    assert capabilities["public_python_api"]["spawn_agent"] == "not_exposed"
    assert capabilities["spawn_agent"] == "not_exposed"
    assert capabilities["runtime_config_harness"]["native_subagents_supported"] is True
    assert capabilities["runtime_config_harness"]["observed_item_types"] == ["collabAgentToolCall", "collabToolCall", "contextCompaction"]
    assert "not missing runtime functionality" in capabilities["tools"]
