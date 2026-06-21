import re

PATTERNS = [
    r"(\d+)\s*(?:years?|năm)\s*(?:of)?\s*(?:experience|kinh nghiệm)?",
]


def extract_experience_years(text: str) -> int:
    years_found = []
    for pattern in PATTERNS:
        years_found += [int(m) for m in re.findall(pattern, text, flags=re.IGNORECASE)]
    return max(years_found) if years_found else 0
