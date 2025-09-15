import re

"""Regular expression patterns for detecting various types of hyperlinks.

The URL pattern intentionally excludes common trailing punctuation so that
links such as ``https://example.com.`` are captured without the final period or
comma.
"""

# Pattern to match HTTP and HTTPS URLs while avoiding trailing punctuation.
URL_PATTERN = re.compile(r"https?://[^\s,]+[^\s.,;:!?)]")

# Pattern to match mailto links.
MAILTO_PATTERN = re.compile(r'mailto:[^\s>]+')

# Pattern to match FTP links.
FTP_PATTERN = re.compile(r'ftp://\S+')

# Collection of all available patterns for convenience.
ALL_PATTERNS = [URL_PATTERN, MAILTO_PATTERN, FTP_PATTERN]
