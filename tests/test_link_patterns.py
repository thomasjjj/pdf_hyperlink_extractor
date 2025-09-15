import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import link_patterns


def test_url_with_fragment():
    text = "See https://example.com/path#section for details"
    assert link_patterns.URL_PATTERN.findall(text) == ["https://example.com/path#section"]


def test_url_with_query_parameters():
    text = "Search at https://example.com/search?q=openai&lang=en"
    assert link_patterns.URL_PATTERN.findall(text) == ["https://example.com/search?q=openai&lang=en"]


def test_url_with_uncommon_characters():
    text = "Try https://example.com/~user/file(name)_-+ for more"
    assert link_patterns.URL_PATTERN.findall(text) == [
        "https://example.com/~user/file(name)_-+"
    ]
