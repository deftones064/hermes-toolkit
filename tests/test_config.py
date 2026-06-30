from toolkit.config import parse_value


def test_parse_value_bool():
    assert parse_value("true") is True
    assert parse_value("false") is False


def test_parse_value_none():
    assert parse_value("none") is None
    assert parse_value("null") is None


def test_parse_value_number():
    assert parse_value("30") == 30
    assert parse_value("0.5") == 0.5


def test_parse_value_string():
    assert parse_value("qwen/qwen3-coder") == "qwen/qwen3-coder"
