"""PWA (Progressive Web App) 지원 모듈.

HTML 보고서를 모바일에서 "홈 화면 추가" 시 앱처럼 실행되도록 한다.
- manifest.json: 앱 이름/아이콘/테마색 정의
- sw.js (service worker): 오프라인 캐시 → 재방문 시 네트워크 없이 열림
- <head> 메타 태그: manifest 링크 + iOS apple-mobile-web-app-* 태그

write_output() 에서 manifest.json + sw.js 를 HTML과 같은 폴더에 저장하면 완성.
"""
from __future__ import annotations

import json
from typing import Any


def gen_pwa_meta_tags(config: Any) -> str:
    """<head>에 삽입할 PWA 메타 태그 HTML 문자열.

    manifest.json 링크 + apple-mobile-web-app 태그를 포함한다.
    """
    company = getattr(config, "company_name", "CUFA Report")
    return (
        '<link rel="manifest" href="manifest.json">\n'
        '<meta name="theme-color" content="#7c6af7">\n'
        '<meta name="mobile-web-app-capable" content="yes">\n'
        '<meta name="apple-mobile-web-app-capable" content="yes">\n'
        f'<meta name="apple-mobile-web-app-title" content="{company}">\n'
        '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
        "<script>\n"
        "if('serviceWorker' in navigator){"
        "navigator.serviceWorker.register('sw.js').catch(()=>{});}\n"
        "</script>\n"
    )


def gen_manifest(config: Any) -> str:
    """manifest.json 내용 (문자열).

    Args:
        config: StockConfig — company_name, stock_code 사용.

    Returns:
        JSON 문자열.
    """
    company = getattr(config, "company_name", "CUFA Report")
    stock_code = getattr(config, "stock_code", "")
    name = f"{company} ({stock_code}) — CUFA 보고서" if stock_code else f"{company} — CUFA 보고서"
    short_name = company[:12] if len(company) > 12 else company

    manifest: dict = {
        "name": name,
        "short_name": short_name,
        "description": "Luxon AI × CUFA 기업분석보고서 — HF/Quant 실행가능성 중심",
        "start_url": ".",
        "display": "standalone",
        "background_color": "#0a0a0a",
        "theme_color": "#7c6af7",
        "orientation": "any",
        "icons": [
            {
                "src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
                       "viewBox='0 0 192 192'%3E%3Crect width='192' height='192' "
                       "rx='24' fill='%237c6af7'/%3E%3Ctext x='96' y='120' "
                       "font-size='96' text-anchor='middle' fill='white'%3EC%3C/text%3E%3C/svg%3E",
                "sizes": "192x192",
                "type": "image/svg+xml",
                "purpose": "any maskable",
            }
        ],
    }
    return json.dumps(manifest, ensure_ascii=False, indent=2)


def gen_service_worker() -> str:
    """sw.js 내용 (문자열).

    Cache-first 전략: 설치 시 핵심 리소스를 캐시,
    이후 fetch는 캐시 우선 → 없으면 네트워크.
    HTML 파일 자체는 항상 네트워크 우선으로 최신성 유지.
    """
    return """\
const CACHE = 'cufa-v1';
const OFFLINE_ASSETS = ['.'];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(OFFLINE_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  // HTML: network-first (항상 최신 보고서)
  if (e.request.mode === 'navigate' || url.pathname.endsWith('.html')) {
    e.respondWith(
      fetch(e.request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
          return res;
        })
        .catch(() => caches.match(e.request))
    );
    return;
  }
  // 나머지: cache-first
  e.respondWith(
    caches.match(e.request).then(cached =>
      cached || fetch(e.request).then(res => {
        const clone = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, clone));
        return res;
      })
    )
  );
});
"""
