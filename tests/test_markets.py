from deriv_advisor.markets import display_name, normalize_symbols


def test_display_name_for_known_index():
    assert display_name("R_75") == "Volatility 75 Index"
    assert display_name("BOOM1000") == "Boom 1000 Index"


def test_normalize_symbols_aliases_and_dedupe():
    symbols = normalize_symbols("r_75, BOOM, boom1000, vol100")
    assert symbols == ["R_75", "BOOM1000", "R_100"]
