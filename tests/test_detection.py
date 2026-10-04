import pytest

from pdf_hyperlink_extractor.link_patterns import find_links


@pytest.mark.parametrize(
    "text, expected",
    [
        ("No links here", []),
        ("https://a", ["https://a"]),
        (
            'See <https://example.com> and "http://example.org".',
            ["https://example.com", "http://example.org"],
        ),
        ("“https://example.com/path”", ["https://example.com/path"]),
        ("(https://example.com/a(foo)).", ["https://example.com/a(foo)"]),
        ("[https://example.com/a[1]].", ["https://example.com/a[1]"]),
        ("https://example.com/path?!;:", ["https://example.com/path"]),
        (
            "https://example.com/search?q=a,b&lang=en#section",
            ["https://example.com/search?q=a,b&lang=en#section"],
        ),
        (
            "HTTP://EXAMPLE.COM MailTo:user@example.com FTP://example.com/file,",
            ["HTTP://EXAMPLE.COM", "MailTo:user@example.com", "FTP://example.com/file"],
        ),
        (
            "mailto:user@example.com?subject=Hello%20there.",
            ["mailto:user@example.com?subject=Hello%20there"],
        ),
        ("https://example.com/über?q=%E2%9C%93", ["https://example.com/über?q=%E2%9C%93"]),
        (
            "https://example.com\nhttps://example.org",
            ["https://example.com", "https://example.org"],
        ),
        ("https:// ftp:// mailto: https://...", []),
    ],
)
def test_link_detection(text, expected):
    assert list(find_links(text)) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        (
            "https://example.com,https://example.org;mailto:a@example.com",
            ["https://example.com", "https://example.org", "mailto:a@example.com"],
        ),
        (
            "https://example.com/?redirect=https://other.example/path",
            ["https://example.com/?redirect=https://other.example/path"],
        ),
        ("'https://example.com/O'Reilly'", ["https://example.com/O'Reilly"]),
        ("{https://example.com/a{1}}.", ["https://example.com/a{1}"]),
        ("(https://example.com/path).).", ["https://example.com/path"]),
    ],
)
def test_prose_link_boundaries(text, expected):
    assert list(find_links(text)) == expected


def test_large_unbalanced_bracket_suffix():
    assert list(find_links("https://example.com" + ")" * 10000)) == ["https://example.com"]
