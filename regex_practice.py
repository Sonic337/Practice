"""
Regex practice in Python — practical patterns with explanations and sample data.

Run: python regex_practice.py
"""

import re


def section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(title)
    print("=" * 60)


def show_matches(label: str, matches: list[str]) -> None:
    if matches:
        for i, m in enumerate(matches, 1):
            print(f"  {i}. {m}")
    else:
        print(f"  (no {label} found)")


# ---------------------------------------------------------------------------
# 1. Extract emails from text
# ---------------------------------------------------------------------------
section("1. Extracting emails")

# Pattern breakdown:
#   [a-zA-Z0-9._%+-]+  local part: letters, digits, and common symbols
#   @                  literal separator
#   [a-zA-Z0-9.-]+     domain name (e.g. gmail, company.co)
#   \.                 literal dot before TLD
#   [a-zA-Z]{2,}       top-level domain (com, io, etc.) — at least 2 letters

EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)

email_text = """
Contact us at support@example.com or sales@company.io.
For urgent issues, reach priya.sharma+work@gmail.com.
Invalid examples: not-an-email, user@, @missing-local.com
"""

print("Pattern:", EMAIL_PATTERN.pattern)
print("\nSample text:", email_text.strip())
print("\nMatches:")
show_matches("emails", EMAIL_PATTERN.findall(email_text))


# ---------------------------------------------------------------------------
# 2. Extract phone numbers
# ---------------------------------------------------------------------------
section("2. Extracting phone numbers")

# Pattern breakdown (US/international-friendly):
#   (?:\+?\d{1,3}[\s.-]?)?   optional country code (+1, +91, etc.)
#   \(?\d{3}\)?              area code, with or without parentheses
#   [\s.-]?                  optional separator (space, dot, dash)
#   \d{3}                    next 3 digits
#   [\s.-]?                  optional separator
#   \d{4}                    last 4 digits

PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"
)

phone_text = """
Call (555) 123-4567 or +1-800-555-0199 for support.
International: +91 98765 43210, +44 20 7946 0958.
Also works: 555.987.6543 and plain 5558675309.
Not phones: 12345, order #9876543210
"""

print("Pattern:", PHONE_PATTERN.pattern)
print("\nSample text:", phone_text.strip())
print("\nMatches:")
show_matches("phone numbers", PHONE_PATTERN.findall(phone_text))


# ---------------------------------------------------------------------------
# 3. Validate URLs
# ---------------------------------------------------------------------------
section("3. Validating URLs")

# Pattern breakdown:
#   https?://                  http or https scheme
#   (?:www\.)?                 optional www.
#   [a-zA-Z0-9-]+              domain label
#   (?:\.[a-zA-Z0-9-]+)+       one or more dot-separated labels (.com, .co.uk)
#   (?::\d+)?                  optional port (:8080)
#   (?:/[^\s]*)?               optional path/query fragment (no whitespace)

URL_PATTERN = re.compile(
    r"https?://(?:www\.)?"
    r"(?:localhost|[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+)"
    r"(?::\d+)?(?:/[^\s]*)?"
)

url_candidates = [
    "https://www.example.com/path?q=1",
    "http://docs.python.org/3/library/re.html",
    "https://github.com/user/repo",
    "ftp://old-protocol.com",           # invalid — wrong scheme
    "not a url",
    "www.bare-domain.com",              # invalid — missing scheme
    "https://localhost:8080/api/v1",
]

print("Pattern:", URL_PATTERN.pattern)
print("\nValidation results:")
for candidate in url_candidates:
    is_valid = bool(URL_PATTERN.fullmatch(candidate))
    status = "VALID" if is_valid else "invalid"
    print(f"  [{status:7}] {candidate}")


# ---------------------------------------------------------------------------
# 4. Find hashtags in social media text
# ---------------------------------------------------------------------------
section("4. Finding hashtags")

# Pattern breakdown:
#   (?<!\w)        negative lookbehind — # must not follow a word character
#                  (avoids matching email#fragment inside addresses)
#   #              literal hash symbol
#   [a-zA-Z0-9_]+  hashtag body: letters, digits, underscores (no spaces)

HASHTAG_PATTERN = re.compile(r"(?<!\w)#[a-zA-Z0-9_]+")

social_text = """
Just shipped v2.0! #Python #regex #100DaysOfCode
Trending: #AI_ML #OpenSource #devlife
Edge cases: #, # spaced tag, email#not-a-tag@here.com
"""

print("Pattern:", HASHTAG_PATTERN.pattern)
print("\nSample text:", social_text.strip())
print("\nMatches:")
show_matches("hashtags", HASHTAG_PATTERN.findall(social_text))


# ---------------------------------------------------------------------------
# 5. Extract crypto wallet addresses
# ---------------------------------------------------------------------------
section("5. Extracting crypto wallet addresses")

# Bitcoin (Legacy / P2SH / Bech32):
#   (?<![0-9a-fA-Fx])  not preceded by hex chars (avoids matching inside ETH addresses)
#   (?:bc1|[13])...    bc1... or 1... / 3... base58-style
#
# Ethereum:
#   0x[a-fA-F0-9]{40}  0x + exactly 40 hex characters

BTC_PATTERN = re.compile(r"(?<![0-9a-fA-Fx])(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}")
ETH_PATTERN = re.compile(r"0x[a-fA-F0-9]{40}")

crypto_text = """
Send BTC to 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa or bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh.
ETH donations: 0x742d35Cc6634C0532925a3b844Bc454e4438f44e
Fake/invalid: 0xSHORT, 1Bad0OIl (contains O and I — not base58)
"""

print("BTC pattern:", BTC_PATTERN.pattern)
print("ETH pattern:", ETH_PATTERN.pattern)
print("\nSample text:", crypto_text.strip())

btc_matches = BTC_PATTERN.findall(crypto_text)
eth_matches = ETH_PATTERN.findall(crypto_text)

print("\nBitcoin addresses:")
show_matches("BTC addresses", btc_matches)
print("\nEthereum addresses:")
show_matches("ETH addresses", eth_matches)


# ---------------------------------------------------------------------------
# Bonus: combining patterns with re.finditer for context
# ---------------------------------------------------------------------------
section("Bonus — finditer with match positions")

mixed_text = (
    "Email me at dev@startup.io or DM @team. "
    "Visit https://startup.io/jobs #hiring "
    "BTC: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
)

COMBINED = [
    ("email", EMAIL_PATTERN),
    ("url", URL_PATTERN),
    ("hashtag", HASHTAG_PATTERN),
    ("btc", BTC_PATTERN),
]

print("Text:", mixed_text)
print("\nAll matches with span (start, end):")
for kind, pattern in COMBINED:
    for match in pattern.finditer(mixed_text):
        print(f"  {kind:8} {match.group()!r}  at {match.span()}")
