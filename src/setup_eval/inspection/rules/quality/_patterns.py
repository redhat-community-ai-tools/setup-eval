from __future__ import annotations

import re

TAUTOLOGICAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("write clean code", re.compile(r"write\s+clean[\s,]+readable\s+code", re.I)),
    ("be helpful", re.compile(r"be\s+helpful\s+and\s+thorough", re.I)),
    ("follow best practices", re.compile(r"follow\s+(the\s+)?best\s+practices", re.I)),
    ("think step by step", re.compile(r"think\s+step\s+by\s+step", re.I)),
    ("consider edge cases", re.compile(r"consider\s+(all\s+)?edge\s+cases", re.I)),
    (
        "handle errors properly",
        re.compile(r"handle\s+errors\s+(?:properly|correctly|gracefully)", re.I),
    ),
    ("use proper formatting", re.compile(r"use\s+proper\s+formatting", re.I)),
    ("write maintainable code", re.compile(r"write\s+maintainable\s+code", re.I)),
    ("be concise", re.compile(r"be\s+concise\s+and\s+clear", re.I)),
    ("ensure code quality", re.compile(r"ensure\s+(?:code\s+)?quality", re.I)),
    (
        "write well-documented code",
        re.compile(r"write\s+well[- ]documented\s+code", re.I),
    ),
    ("be thorough", re.compile(r"be\s+thorough\s+(?:in|and|with)", re.I)),
    ("validate user input", re.compile(r"(?:always\s+)?validate\s+(?:all\s+)?user\s+input", re.I)),
    (
        "keep functions small",
        re.compile(r"keep\s+(?:functions|methods)\s+(?:small|short|focused)", re.I),
    ),
    ("separate concerns", re.compile(r"separate\s+(?:your\s+)?concerns", re.I)),
    (
        "use meaningful names",
        re.compile(
            r"use\s+(?:meaningful|descriptive|clear)\s+(?:variable\s+)?names",
            re.I,
        ),
    ),
    ("avoid magic numbers", re.compile(r"avoid\s+(?:using\s+)?magic\s+numbers", re.I)),
    ("write unit tests", re.compile(r"(?:always\s+)?write\s+(?:unit\s+)?tests", re.I)),
    ("document your code", re.compile(r"document\s+(?:your\s+)?(?:code|changes)", re.I)),
    ("review your changes", re.compile(r"review\s+(?:your\s+)?changes", re.I)),
    (
        "make sure code compiles",
        re.compile(r"make\s+sure\s+(?:your\s+)?code\s+(?:compiles|builds)", re.I),
    ),
    ("DRY principle", re.compile(r"follow\s+(?:the\s+)?DRY\s+principle", re.I)),
    (
        "use version control",
        re.compile(r"(?:always\s+)?use\s+(?:proper\s+)?version\s+control", re.I),
    ),
    (
        "keep code organized",
        re.compile(r"keep\s+(?:your\s+)?code\s+(?:organized|structured|tidy)", re.I),
    ),
]

_SPECIFICITY_MARKERS = re.compile(
    r"(?:"
    r"`[^`]+`"  # backtick-quoted terms
    r"|\.(?:py|ts|js|tsx|jsx|rs|go|rb|java|yaml|yml|toml|json|md)\b"  # file extensions
    r"|(?:^|[\s(])\.?/"  # path-like strings
    r")",
    re.M,
)


def has_project_specificity(line: str) -> bool:
    return bool(_SPECIFICITY_MARKERS.search(line))
