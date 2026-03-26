# /scrape — 웹 스크래핑 (Scrapling)

Scrapling을 사용해 봇 탐지 우회 + 적응형 웹 스크래핑.

## 사용법
```
/scrape [URL] [--selector CSS선택자] [--text] [--links]
```

## 실행 방법

```python
from scrapling import Fetcher

fetcher = Fetcher()
page = fetcher.get("https://example.com")

# 텍스트 추출
text = page.get_all_text()

# CSS 선택자로 추출
items = page.css("h2.title")
for item in items:
    print(item.text)

# 링크 추출
links = page.css("a")
for link in links:
    print(link.attrib.get("href", ""))
```

## 특징
- 봇 탐지 완전 우회 (Cloudflare 네이티브)
- BeautifulSoup 대비 774배 빠름
- 웹사이트 구조 변경에 자동 적응
- Playwright 기반 실제 브라우저 자동화

## 에이전트 연동
DOGE가 뉴스 수집 시 사용:
```python
from scrapling import Fetcher
fetcher = Fetcher()
page = fetcher.get("https://news.example.com/rss")
articles = page.css("article")
```
