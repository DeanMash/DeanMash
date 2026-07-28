from deriv_advisor.analyzer import analyze_instagram
from deriv_advisor.instagram_client import InstagramPost, extract_instagram_urls, _parse_meta


def test_extract_instagram_urls():
    text = "see https://www.instagram.com/reel/AbC123xyz/ and https://instagram.com/p/ZZZ999/"
    urls = extract_instagram_urls(text)
    assert "https://www.instagram.com/reel/AbC123xyz/" in urls
    assert "https://instagram.com/p/ZZZ999/" in urls


def test_parse_meta_og_description():
    html = '''
    <html><head>
      <meta property="og:title" content="Trader on Instagram" />
      <meta property="og:description" content="Volatility 75 CALL setup bullish breakout" />
    </head></html>
    '''
    meta = _parse_meta(html)
    assert "volatility 75" in meta["og:description"].lower()


def test_analyze_instagram_detects_call_and_symbol():
    posts = [
        InstagramPost(
            url="https://www.instagram.com/reel/AbC123xyz/",
            caption="Volatility 75 look bullish, strong CALL breakout setup",
            title="sig",
            author="trader",
            media_type="reel",
            fetched=True,
            note="ok",
        )
    ]
    signal = analyze_instagram(posts)
    assert signal.fetched_count == 1
    assert signal.direction_hint == "CALL"
    assert "R_75" in signal.matched_symbols
    assert signal.score > 0
