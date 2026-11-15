"""A thin MCP surface over the generated workflow, not over individual agents."""

import json
import hashlib
import re
from pathlib import Path

from mcp.server.mcpserver import Context, MCPServer
from mcp.types import CallToolResult, TextContent
if __package__:
    from .workflow import SPEC, run, verify_state
    from .execution import state_directory
else:
    from workflow import SPEC, run, verify_state
    from execution import state_directory


def server_for(state_dir, approval_handler=None):
    state_dir = Path(state_dir)
    server = MCPServer("generated-codex-workflow", instructions="Run the workflow as a single task-level service. Internal agents are not independent public services.")
    writes = any(agent["sandbox"] == "workspace_write" for agent in SPEC["agents"]) or any(tool["side_effect"] for tool in SPEC["tools"])

    def reply(value):
        return CallToolResult(content=[TextContent(type="text", text=json.dumps(value))], structured_content=value, is_error=value.get("status") in {"failed", "blocked", "outcome_unknown", "partial"})

    def state_path(run_id):
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", run_id):
            raise ValueError("Invalid run ID")
        return state_dir / f"{run_id}.json"

    async def invoke(operation, request, run_id, ctx):
        try:
            path = state_path(run_id)
        except ValueError as exc:
            return reply({"status": "blocked", "error": {"code": "invalid_input", "message": str(exc)}})
        if not writes:
            return reply(await operation(request, state_path=path))
        if approval_handler is None:
            return reply({"status": "blocked", "error": {"code": "approval_channel_unavailable", "message": "No host-trusted human approval handler is configured; workflow was not executed"}})
        try:
            request_hash = hashlib.sha256(json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            details = {"operation": operation.__name__, "run_id": run_id, "spec_revision": SPEC["revision"], "request_sha256": request_hash, "message": f"Human approval is required for {operation.__name__} run {run_id!r} at spec revision {SPEC['revision']} with request SHA-256 {request_hash}. This invocation may write to the workspace or use side-effect tools. Approve only this exact invocation."}
            approved = await approval_handler(ctx, details)
        except Exception:
            return reply({"status": "blocked", "error": {"code": "approval_channel_unavailable", "message": "Client cannot present human confirmation; workflow was not executed"}})
        if approved is not True:
            return reply({"status": "blocked", "error": {"code": "permission_denied", "message": "Human approval was not granted; workflow was not executed"}})
        return reply(await operation(request, state_path=path, approve_writes=True))

    @server.tool()
    async def mas_run(request: dict, run_id: str = "latest", ctx: Context = None) -> CallToolResult:
        return await invoke(run, request, run_id, ctx)

    @server.tool()
    async def mas_recover(request: dict, run_id: str = "latest", ctx: Context = None) -> CallToolResult:
        if __package__:
            from .workflow import recover
        else:
            from workflow import recover
        return await invoke(recover, request, run_id, ctx)

    @server.tool()
    def mas_status(run_id: str = "latest") -> CallToolResult:
        return reply(json.loads(state_path(run_id).read_text()))

    @server.tool()
    def mas_read(run_id: str = "latest") -> CallToolResult:
        state = json.loads(state_path(run_id).read_text())
        return reply({"status": state["status"], "output": state.get("output"), "packets": state["packets"]})

    @server.tool()
    def mas_verify(run_id: str = "latest") -> CallToolResult:
        from jsonschema import Draft202012Validator

        state = json.loads(state_path(run_id).read_text())
        if state.get("status") != "passed":
            return reply({"status": "failed", "reason": "Workflow has not passed"})
        verify_state(state, state.get("request"))
        return reply({"status": "passed", "run_id": run_id, "spec_revision": SPEC["revision"]})

    return server


def serve(state_dir, approval_handler=None):
    server_for(state_dir, approval_handler=approval_handler).run(transport="stdio")


if __name__ == "__main__":
    serve(state_directory(Path(__file__).resolve().parent))
