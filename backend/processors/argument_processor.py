from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Claim:
    text: str
    evidence: str | None = None


def split_sentences(text: str) -> list[str]:
    chunks = re.split(r'(?<=[.!?])\s+', text.strip())
    return [c.strip() for c in chunks if c.strip()]


def extract_claims_from_lines(raw: str) -> list[str]:
    lines = [line.strip() for line in raw.split('\n') if line.strip()]
    claims = [line[1:].strip() for line in lines if line.startswith('-')]
    return [c for c in claims if c]


def detect_fallacy(text: str, claims: list[Claim]) -> str:
    lowered = text.lower()
    if 'either' in lowered and ' or ' in lowered:
        return 'FALSE_DICHOTOMY'
    if any('because' in c.text.lower() or 'since' in c.text.lower() for c in claims):
        if any(c.evidence == 'ASSERTED' for c in claims):
            return 'FALSE_CAUSATION'
    if any(word in lowered for word in ['all', 'always', 'never', 'everyone']):
        if all(c.evidence == 'ASSERTED' for c in claims if c.evidence):
            return 'HASTY_GENERALIZATION'
    if 'experts say' in lowered or 'studies show' in lowered:
        return 'APPEAL_TO_AUTHORITY'
    return 'UNCLEAR'


def pick_verification_line(claims: list[Claim]) -> str:
    for claim in claims:
        if claim.evidence == 'ASSERTED':
            return f'Check the original text for this claim: "{claim.text}". No evidence is provided.'
    return 'Verify the highlighted claims against the original text.'
