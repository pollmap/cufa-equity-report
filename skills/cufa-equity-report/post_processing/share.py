"""CUFA 보고서 공유/배포 헬퍼.

생성된 HTML 보고서를 빠르게 공유하는 3가지 방법:
1. 로컬 HTTP 서버 — 브라우저에서 즉시 확인
2. 경로 복사 — 파일 탐색기/Discord/카카오톡에 붙여넣기용
3. ZIP 패키지 — HTML + manifest.json + sw.js를 한 파일로 압축

사용법:
    from post_processing.share import serve_local, copy_path, zip_report
    serve_local(html_path, port=8080)          # 브라우저 열림
    clip = copy_path(html_path)                # 경로 반환
    zip_path = zip_report(html_path)           # .zip 생성
"""
from __future__ import annotations

import os
import sys
import threading
import webbrowser
import zipfile
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


def serve_local(html_path: Path | str, port: int = 8080) -> str:
    """로컬 HTTP 서버를 백그라운드 스레드로 실행하고 브라우저를 연다.

    PWA/Service Worker는 file:// 프로토콜에서 작동하지 않는다.
    HTTP 서버를 통해야 manifest + SW가 정상 작동한다.

    Args:
        html_path: 서빙할 HTML 파일 경로.
        port: 로컬 포트 (기본 8080).

    Returns:
        접속 URL 문자열.
    """
    html_path = Path(html_path)
    serve_dir = html_path.parent
    file_name = html_path.name
    url = f"http://localhost:{port}/{file_name}"

    class _Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(serve_dir), **kwargs)

        def log_message(self, fmt, *args):  # 콘솔 로그 억제
            pass

    def _run():
        server = HTTPServer(("", port), _Handler)
        server.serve_forever()

    t = threading.Thread(target=_run, daemon=True)
    t.start()

    webbrowser.open(url)
    print(f"[CUFA Share] 서버 시작: {url}")
    print("[CUFA Share] 종료하려면 프로세스를 중단하세요 (Ctrl+C)")
    return url


def copy_path(html_path: Path | str) -> str:
    """HTML 파일 절대경로를 반환하고 클립보드에 복사한다 (Windows/Mac).

    Discord, KakaoTalk, VS Code 등에 직접 붙여넣기할 때 사용.

    Args:
        html_path: HTML 파일 경로.

    Returns:
        절대경로 문자열.
    """
    abs_path = str(Path(html_path).resolve())

    try:
        if sys.platform == "win32":
            os.system(f'echo {abs_path}| clip')
        elif sys.platform == "darwin":
            os.system(f'echo "{abs_path}" | pbcopy')
        # Linux는 xclip 필요 — 생략
    except Exception:
        pass  # 클립보드 실패해도 경로는 반환

    print(f"[CUFA Share] 경로 복사됨: {abs_path}")
    return abs_path


def zip_report(html_path: Path | str, out_path: Path | str | None = None) -> Path:
    """HTML + PWA 보조 파일을 ZIP으로 묶는다.

    같은 폴더의 manifest.json + sw.js 도 포함한다.
    zip 파일은 Discord/이메일로 전송하기 쉽다.

    Args:
        html_path: HTML 파일 경로.
        out_path: 출력 ZIP 경로. 지정하지 않으면 같은 폴더에 동일 파일명.zip 생성.

    Returns:
        생성된 ZIP 파일 Path.
    """
    html_path = Path(html_path)
    if out_path is None:
        out_path = html_path.with_suffix(".zip")
    out_path = Path(out_path)

    companion_files = ["manifest.json", "sw.js"]

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(html_path, html_path.name)
        for fname in companion_files:
            fpath = html_path.parent / fname
            if fpath.exists():
                zf.write(fpath, fname)

    size_kb = out_path.stat().st_size // 1024
    print(f"[CUFA Share] ZIP 생성: {out_path} ({size_kb} KB)")
    return out_path
