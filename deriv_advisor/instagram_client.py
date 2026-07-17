from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from html import unescape
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

INSTAGRAM_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:instagram\.com|instagr\.am)/(?:p|reel|reels|tv)/[A-Za-z0-9_-]+/?",
    re.IGNORECASE,
)

_META_RE = re.compile(
    r'<meta[^>]+(?:property|name)=["\']([^"\']+)["\'][^>]+content=["\']([^"\']*)["\'][^>]*>',
    re.IGNORECASE,
)
_META_RE_ALT = re.compile(
    r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+(?:property|name)=["\']([^"\']+)["\'][^>]*>',
    re.IGNORECASE,
)


@dataclass
class InstagramPost:
    url: str
    caption: str
    title: str
    author: str | None
    media_type: str  # post / reel / unknown
    fetched: bool
    note: str


def extract_instagram_urls(text: str) -> list[str]:
    found = INSTAGRAM_URL_RE.findall(text or "")
    # Normalize trailing punctuation common in chat pastes.
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in found:
        url = raw.rstrip(").,]>'\"")
        key = url.split("?")[0].rstrip("/").lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(url)
    return cleaned


def _media_type_from_url(url: str) -> str:
    path = urlparse(url).path.lower()
    if "/reel" in path:
        return "reel"
    if "/tv/" in path:
        return "tv"
    if "/p/" in path:
        return "post"
    return "unknown"


def _parse_meta(html: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    for match in _META_RE.finditer(html):
        meta[match.group(1).lower()] = unescape(match.group(2)).strip()
    for match in _META_RE_ALT.finditer(html):
        meta[match.group(2).lower()] = unescape(match.group(1)).strip()
    return meta


def _fetch_via_oembed(url: str, access_token: str) -> InstagramPost | None:
    endpoint = "https://graph.facebook.com/v19.0/instagram_oembed"
    try:
        response = requests.get(
            endpoint,
            params={"url": url, "access_token": access_token, "omitscript": "true"},
            timeout=20,
        )
        if response.status_code != 200:
            logger.info("Instagram oEmbed failed (%s): %s", response.status_code, response.text[:200])
            return None
        payload = response.json()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Instagram oEmbed error for %s: %s", url, exc)
        return None

    title = str(payload.get("title") or "").strip()
    author = str(payload.get("author_name") or "").strip() or None
    caption = title
    if not caption:
        return InstagramPost(
            url=url,
            caption="",
            title="",
            author=author,
            media_type=_media_type_from_url(url),
            fetched=False,
            note="oEmbed returned no caption text.",
        )
    return InstagramPost(
        url=url,
        caption=caption,
        title=title[:120],
        author=author,
        media_type=_media_type_from_url(url),
        fetched=True,
        note="Caption loaded via Instagram oEmbed.",
    )


def _fetch_via_page_meta(url: str) -> InstagramPost:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        html = response.text or ""
    except Exception as exc:  # noqa: BLE001
        logger.warning("Instagram page fetch failed for %s: %s", url, exc)
        return InstagramPost(
            url=url,
            caption="",
            title="",
            author=None,
            media_type=_media_type_from_url(url),
            fetched=False,
            note=f"Could not fetch link preview ({exc}).",
        )

    meta = _parse_meta(html)
    title = meta.get("og:title") or meta.get("twitter:title") or ""
    description = meta.get("og:description") or meta.get("twitter:description") or ""
    caption = description or title
    author = None
    if title and " on Instagram" in title:
        author = title.split(" on Instagram", 1)[0].strip() or None

    if not caption:
        return InstagramPost(
            url=url,
            caption="",
            title=title[:120],
            author=author,
            media_type=_media_type_from_url(url),
            fetched=False,
            note=(
                "Instagram did not expose caption text (login wall or private post). "
                "Try a public post, or set FACEBOOK_ACCESS_TOKEN for oEmbed."
            ),
        )

    return InstagramPost(
        url=url,
        caption=caption.strip(),
        title=(title or caption)[:120],
        author=author,
        media_type=_media_type_from_url(url),
        fetched=True,
        note="Caption loaded from public link preview metadata.",
    )


def fetch_instagram_post(url: str, facebook_access_token: str | None = None) -> InstagramPost:
    if facebook_access_token:
        oembed = _fetch_via_oembed(url, facebook_access_token)
        if oembed and oembed.fetched:
            return oembed
    return _fetch_via_page_meta(url)


def fetch_instagram_posts(
    urls: list[str],
    facebook_access_token: str | None = None,
) -> list[InstagramPost]:
    posts: list[InstagramPost] = []
    for url in urls:
        posts.append(fetch_instagram_post(url, facebook_access_token=facebook_access_token))
    return posts
