"""CUFA Preflight — Nexus MCP 표준 클라이언트.

Streamable HTTP + SSE 헤더 필수. SKILL.md §10.2 구현체.
"""
from __future__ import annotations

import json
import re
import subprocess
from typing import Any, Protocol

from .tool_schemas import validate_args

NEXUS_MCP_URL = __import__("os").environ.get("NEXUS_MCP_URL", "")
KIS_BACKTEST_URL = "http://127.0.0.1:3846/mcp"

SSE_HEADERS: tuple[str, ...] = (
    "-H", "Content-Type: application/json",
    "-H", "Accept: application/json, text/event-stream",
)


class MCPClient(Protocol):
    """MCP 클라이언트 인터페이스 — 의존성 주입용."""

    def call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]: ...


class MCPError(RuntimeError):
    """MCP 호출 실패."""


class NexusMCPClient:
    """Nexus Finance MCP (VPS <MCP_VPS_HOST>) 클라이언트.

    - Streamable HTTP + SSE 응답 파싱
    - 호출 전 `tool_schemas`로 인자 검증
    - isError 응답 시 `MCPError` 발생
    """

    def __init__(self, url: str = NEXUS_MCP_URL, timeout: int = 30) -> None:
        self.url = url
        self.timeout = timeout
        self._call_id = 0

    def call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        validate_args(tool_name, arguments)

        self._call_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._call_id,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }
        proc = subprocess.run(
            [
                "curl", "-s", "-m", str(self.timeout),
                self.url, "-X", "POST",
                *SSE_HEADERS,
                "-d", json.dumps(payload, ensure_ascii=False),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if proc.returncode != 0:
            raise MCPError(f"curl 실패: rc={proc.returncode}, stderr={proc.stderr[:300]}")

        match = re.search(r"data:\s*(\{.*\})", proc.stdout, re.DOTALL)
        if not match:
            raise MCPError(f"SSE 응답 파싱 실패: {proc.stdout[:500]}")

        data = json.loads(match.group(1))
        if "error" in data:
            raise MCPError(f"MCP 프로토콜 에러: {data['error']}")

        result = data.get("result", {})
        if result.get("isError"):
            err_text = result.get("content", [{}])[0].get("text", "")
            raise MCPError(f"MCP 도구 에러 ({tool_name}): {err_text[:500]}")

        content = result.get("content", [])
        if not content:
            return {}

        # content[0].text는 JSON 문자열 → 한 번 더 파싱
        first_text = content[0].get("text", "")
        try:
            return json.loads(first_text)
        except json.JSONDecodeError:
            # 일부 도구는 raw text 반환
            return {"_raw": first_text}

    def initialize(self) -> dict[str, Any]:
        """프로토콜 initialize 호출 (selftest용)."""
        self._call_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._call_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "cufa-preflight", "version": "15.0"},
            },
        }
        proc = subprocess.run(
            ["curl", "-s", "-m", str(self.timeout), self.url, "-X", "POST",
             *SSE_HEADERS, "-d", json.dumps(payload)],
            capture_output=True, text=True, encoding="utf-8",
        )
        match = re.search(r"data:\s*(\{.*\})", proc.stdout, re.DOTALL)
        if not match:
            raise MCPError(f"initialize 실패: {proc.stdout[:300]}")
        return json.loads(match.group(1))
