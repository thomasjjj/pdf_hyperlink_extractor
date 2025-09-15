import re

"""Regular expression patterns for detecting various types of hyperlinks."""

# Pattern to match HTTP and HTTPS URLs. Matches any non-whitespace characters
# after the protocol to allow for fragments, query parameters and unusual
# path characters.
URL_PATTERN = re.compile(r'https?://\S+')

# Pattern to match mailto links.
MAILTO_PATTERN = re.compile(r'mailto:[^\s>]+')

# Pattern to match FTP links.
FTP_PATTERN = re.compile(r'ftp://\S+')

# Collection of all available patterns for convenience.
ALL_PATTERNS = [URL_PATTERN, MAILTO_PATTERN, FTP_PATTERN]
