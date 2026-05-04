from __future__ import annotations

import re
from itertools import combinations


def extract_defined_terms(text: str) -> dict[str, list[int]]:
    patterns = [
        r'"([A-Z][a-zA-Z\s]{2,30})"',
        r'hereinafter referred to as "([^"]+)"',
        r'\(the "([A-Z][a-zA-Z\s]{1,20})"\)',
    ]
    terms: dict[str, list[int]] = {}
    lines = text.split('\n')
    for pattern in patterns:
        for match in re.findall(pattern, text):
            term = match.strip()
            if len(term) > 2:
                occurrences = [i for i, line in enumerate(lines) if term in line]
                terms[term] = occurrences
    return terms


def segment_clauses(text: str) -> list[dict]:
    section_pattern = r'(?:^|\n)(?:Article\s+\d+|Section\s+[\d.]+|\d+\.|WHEREAS|NOW THEREFORE)'
    splits = re.split(section_pattern, text, flags=re.MULTILINE)
    headers = re.findall(section_pattern, text, flags=re.MULTILINE)
    clauses = []
    for i, content in enumerate(splits):
        if content.strip():
            header = headers[i - 1].strip() if i > 0 and i - 1 < len(headers) else f'Clause {i}'
            clauses.append({'id': i, 'header': header, 'text': content.strip()[:800]})
    return clauses


def build_reference_graph(clauses: list[dict], defined_terms: dict) -> list[tuple[int, int]]:
    clause_terms = {clause['id']: {term for term in defined_terms if term in clause['text']} for clause in clauses}
    pairs = []
    for a, b in combinations(clauses, 2):
        shared = clause_terms[a['id']] & clause_terms[b['id']]
        if shared:
            pairs.append((a['id'], b['id']))
    return pairs
