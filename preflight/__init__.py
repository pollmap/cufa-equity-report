"""CUFA Preflight 모듈 — Phase 0 표준 검증.

공개 API:
    PREFLIGHT           : 기본 임계값 상수 (PreflightThresholds)
    PreflightConfig     : 종목별 입력 구조체
    PreflightResult     : 검증 결과 구조체
    preflight_validate  : 5점 체크 표준 프로토콜
    NexusMCPClient      : Streamable HTTP MCP 클라이언트
    TOOL_SCHEMAS        : MCP 도구 인자 레지스트리
    INDUSTRY_CHECKLIST  : 산업별 필수 항목 레지스트리
    split_cfs_ofs       : DART 응답 연결/별도 분리
    get_account_value   : DART 계정 값 추출
"""
from __future__ import annotations

from .thresholds import PREFLIGHT, PreflightThresholds
from .checker import (
    PreflightConfig,
    PreflightResult,
    preflight_validate,
)
from .mcp_client import MCPClient, NexusMCPClient
from .tool_schemas import TOOL_SCHEMAS, validate_args
from .industry_checklist import INDUSTRY_CHECKLIST
from .dart_parser import split_cfs_ofs, get_account_value

__all__ = [
    "PREFLIGHT",
    "PreflightThresholds",
    "PreflightConfig",
    "PreflightResult",
    "preflight_validate",
    "MCPClient",
    "NexusMCPClient",
    "TOOL_SCHEMAS",
    "validate_args",
    "INDUSTRY_CHECKLIST",
    "split_cfs_ofs",
    "get_account_value",
]
