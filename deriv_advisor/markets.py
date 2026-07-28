from __future__ import annotations

# Human-readable names for common Deriv synthetic indices.
INDEX_DISPLAY_NAMES: dict[str, str] = {
    "R_10": "Volatility 10 Index",
    "R_25": "Volatility 25 Index",
    "R_50": "Volatility 50 Index",
    "R_75": "Volatility 75 Index",
    "R_100": "Volatility 100 Index",
    "1HZ10V": "Volatility 10 (1s) Index",
    "1HZ25V": "Volatility 25 (1s) Index",
    "1HZ50V": "Volatility 50 (1s) Index",
    "1HZ75V": "Volatility 75 (1s) Index",
    "1HZ100V": "Volatility 100 (1s) Index",
    "BOOM300N": "Boom 300 Index",
    "BOOM500": "Boom 500 Index",
    "BOOM1000": "Boom 1000 Index",
    "CRASH300N": "Crash 300 Index",
    "CRASH500": "Crash 500 Index",
    "CRASH1000": "Crash 1000 Index",
    "JD10": "Jump 10 Index",
    "JD25": "Jump 25 Index",
    "JD50": "Jump 50 Index",
    "JD75": "Jump 75 Index",
    "JD100": "Jump 100 Index",
    "RDBEAR": "Bear Market Index",
    "RDBULL": "Bull Market Index",
}

# Default watchlist for new installs — popular synthetics traders usually use.
DEFAULT_SYMBOLS: list[str] = [
    "R_10",
    "R_25",
    "R_50",
    "R_75",
    "R_100",
    "1HZ75V",
    "1HZ100V",
    "BOOM1000",
    "CRASH1000",
    "JD10",
    "JD25",
    "JD50",
    "JD75",
    "JD100",
]


def display_name(symbol: str) -> str:
    return INDEX_DISPLAY_NAMES.get(symbol, symbol)


def normalize_symbols(raw: list[str] | str | None) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        parts = raw.replace("\n", ",").replace(" ", ",").split(",")
    else:
        parts = []
        for item in raw:
            parts.extend(str(item).replace("\n", ",").replace(" ", ",").split(","))

    cleaned: list[str] = []
    seen: set[str] = set()
    for part in parts:
        symbol = part.strip().upper()
        if not symbol:
            continue
        # Allow common aliases from Deriv UI labels.
        aliases = {
            "VOL10": "R_10",
            "VOL25": "R_25",
            "VOL50": "R_50",
            "VOL75": "R_75",
            "VOL100": "R_100",
            "V10": "R_10",
            "V25": "R_25",
            "V50": "R_50",
            "V75": "R_75",
            "V100": "R_100",
            "BOOM": "BOOM1000",
            "CRASH": "CRASH1000",
        }
        symbol = aliases.get(symbol, symbol)
        if symbol not in seen:
            seen.add(symbol)
            cleaned.append(symbol)
    return cleaned
