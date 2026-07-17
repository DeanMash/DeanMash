from __future__ import annotations

import logging
from dataclasses import dataclass

import feedparser
import requests

logger = logging.getLogger(__name__)

# Free RSS sources — no API key required.
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
    "https://news.google.com/rss/search?q=forex+OR+markets+OR+stocks&hl=en-US&gl=US&ceid=US:en",
]


@dataclass
class NewsItem:
    title: str
    summary: str
    source: str
    link: str


def fetch_rss_news(max_items: int = 20) -> list[NewsItem]:
    items: list[NewsItem] = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            source = feed.feed.get("title", url)
            for entry in feed.entries[:8]:
                items.append(
                    NewsItem(
                        title=str(entry.get("title", "")).strip(),
                        summary=str(entry.get("summary", entry.get("description", ""))).strip(),
                        source=str(source),
                        link=str(entry.get("link", "")),
                    )
                )
        except Exception as exc:  # noqa: BLE001 — keep advisor running if one feed fails
            logger.warning("RSS feed failed (%s): %s", url, exc)

    # Deduplicate by title
    seen: set[str] = set()
    unique: list[NewsItem] = []
    for item in items:
        key = item.title.lower()
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(item)
        if len(unique) >= max_items:
            break
    return unique


def fetch_newsapi_headlines(api_key: str, max_items: int = 15) -> list[NewsItem]:
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": api_key,
        "category": "business",
        "language": "en",
        "pageSize": max_items,
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:  # noqa: BLE001
        logger.warning("NewsAPI request failed: %s", exc)
        return []

    items: list[NewsItem] = []
    for article in payload.get("articles", []):
        title = (article.get("title") or "").strip()
        if not title:
            continue
        items.append(
            NewsItem(
                title=title,
                summary=(article.get("description") or "").strip(),
                source=(article.get("source") or {}).get("name", "NewsAPI"),
                link=article.get("url") or "",
            )
        )
    return items


def fetch_news(news_api_key: str | None = None, max_items: int = 20) -> list[NewsItem]:
    items = fetch_rss_news(max_items=max_items)
    if news_api_key:
        api_items = fetch_newsapi_headlines(news_api_key, max_items=max_items)
        # Prefer NewsAPI items first, then fill with RSS.
        merged = api_items + items
        seen: set[str] = set()
        unique: list[NewsItem] = []
        for item in merged:
            key = item.title.lower()
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
            if len(unique) >= max_items:
                break
        return unique
    return items
