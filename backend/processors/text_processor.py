from __future__ import annotations

try:
    from importlib import import_module

    flesch_kincaid_grade = import_module('textstat').flesch_kincaid_grade
except ModuleNotFoundError:  # pragma: no cover - fallback for mismatched runtimes
    def flesch_kincaid_grade(text: str) -> float:
        words = text.split()
        sentences = max(1, text.count('.') + text.count('!') + text.count('?'))
        syllable_estimate = sum(max(1, len(word) // 3) for word in words)
        word_count = max(1, len(words))
        # Lightweight approximation of the Flesch-Kincaid grade level.
        return 0.39 * (word_count / sentences) + 11.8 * (syllable_estimate / word_count) - 15.59


def readability_score(text: str) -> dict:
    words = text.split()
    sentences = max(1, text.count('.') + text.count('!') + text.count('?'))
    jargon = sum(1 for w in words if len(w) > 12)
    return {
        'grade_level': round(flesch_kincaid_grade(text), 2),
        'avg_sentence_len': round(len(words) / sentences, 2),
        'jargon_density': round(jargon / max(1, len(words)), 3),
    }


def word_count(text: str) -> int:
    return len(text.split())


def validate_facts(draft: str, facts: list[str]) -> list[str]:
    sentences = [s.strip() for s in draft.split('.') if s.strip()]
    unsupported = []
    for sentence in sentences:
        if not any(fact.lower() in sentence.lower() for fact in facts):
            unsupported.append(sentence)
    return unsupported


def extract_numbers(text: str) -> list[str]:
    return [token for token in text.replace(',', '').split() if token.replace('.', '').isdigit()]
