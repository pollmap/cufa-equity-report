"""CUFA Builder — Minimal Markdown → HTML 변환기.

보고서 본문에 임베드할 간단한 마크다운 조각(테이블·블록쿼트·단락)을
CSS 클래스가 붙은 HTML로 변환. 외부 라이브러리 없이 스탠드얼론 동작.
"""
from __future__ import annotations

import re
from pathlib import Path


def read_md(path: str | Path) -> str:
    """UTF-8 마크다운 파일을 문자열로 읽는다."""
    return Path(path).read_text(encoding="utf-8")


def md_to_html(md_text: str) -> str:
    """단순 마크다운을 CUFA 스타일 HTML로 변환.

    지원 문법:
    - 테이블 (`| a | b |` 형식)
    - 블록쿼트 (`> ...`) → `<div class="callout">`
    - 단락 (인라인 `**bold**`, `*italic*`)
    - `#` 헤더는 무시 (섹션 헤더는 `helpers.section_header()` 사용)
    - `---` 구분선 무시
    """
    lines = md_text.strip().split("\n")
    parts: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line == "---" or line.startswith("#"):
            i += 1
            continue
        if line.startswith("|"):
            table_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            parts.append(_md_table_to_html(table_lines))
            continue
        if line.startswith(">"):
            quote = line[1:].strip()
            i += 1
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote += " " + lines[i].strip()[1:].strip()
                i += 1
            parts.append(f'<div class="callout"><p>{_md_inline(quote)}</p></div>')
            continue
        parts.append(f"<p>{_md_inline(line)}</p>")
        i += 1
    return "\n".join(parts)


def _md_inline(text: str) -> str:
    """인라인 `**bold**` 와 `*italic*` 만 치환."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def _md_table_to_html(table_lines: list[str]) -> str:
    rows: list[list[str]] = []
    for line in table_lines:
        if re.match(r"^\|[\s\-:|]+\|$", line):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        rows.append(cells)
    if len(rows) < 2:
        return ""
    parts: list[str] = ['<div class="table-scroll"><table class="data"><tr>']
    parts += [f"<th>{_md_inline(h)}</th>" for h in rows[0]]
    parts.append("</tr>")
    for row in rows[1:]:
        parts.append("<tr>")
        parts += [f"<td>{_md_inline(cell)}</td>" for cell in row]
        parts.append("</tr>")
    parts.append("</table></div>")
    return "\n".join(parts)
