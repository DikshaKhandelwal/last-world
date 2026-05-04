from __future__ import annotations

from collections import Counter
import math
import re


def fingerprint_authors(messages: list[dict]) -> dict[str, dict]:
    grouped: dict[str, list[str]] = {}
    for message in messages:
        grouped.setdefault(message.get('author', 'unknown'), []).append(message.get('text', ''))

    output = {}
    for author, texts in grouped.items():
        words = ' '.join(texts).split()
        sentences = max(1, sum(text.count('.') + text.count('?') + text.count('!') for text in texts))
        question_ratio = sum(text.count('?') for text in texts) / max(1, len(texts))
        hedge_count = sum(text.lower().count(word) for text in texts for word in ['maybe', 'perhaps', 'likely', 'possibly'])
        vocab_uniqueness = len(set(words)) / max(1, len(words))
        entity_density = sum(1 for w in words if w[:1].isupper()) / max(1, len(words))
        punctuation_pattern = Counter(ch for text in texts for ch in text if ch in ',;:!?')
        output[author] = {
            'avg_sentence_len': len(words) / sentences,
            'question_ratio': question_ratio,
            'hedge_count': hedge_count,
            'vocab_uniqueness': vocab_uniqueness,
            'entity_density': entity_density,
            'punctuation_pattern': dict(punctuation_pattern),
        }
    return output


def consistency_check(messages: list[dict]) -> dict[str, float]:
    grouped: dict[str, list[str]] = {}
    for message in messages:
        grouped.setdefault(message.get('author', 'unknown'), []).append(message.get('text', ''))
    scores = {}
    for author, texts in grouped.items():
        lower = ' '.join(texts).lower()
        contradictions = sum(lower.count(term) for term in ['not', 'never', 'always', 'must', 'cannot'])
        scores[author] = max(0.0, 1.0 - contradictions / 20.0)
    return scores


def anomaly_score(fingerprints, consistency) -> list[tuple[str, float]]:
    scored = []
    for author, fp in fingerprints.items():
        score = (1 - fp['vocab_uniqueness']) + (1 - consistency.get(author, 1.0)) + fp['hedge_count'] * 0.05
        scored.append((author, round(score, 3)))
    return sorted(scored, key=lambda x: x[1], reverse=True)


def parse_messages(raw: str) -> list[dict]:
    messages = []
    for line in raw.split('\n'):
        if ':' not in line:
            continue
        name, text = line.split(':', 1)
        name = name.strip()
        text = text.strip()
        if name and text:
            messages.append({'author': name, 'text': text})
    return messages


def compute_author_metrics(messages: list[dict]) -> dict[str, dict]:
    grouped: dict[str, list[str]] = {}
    for message in messages:
        grouped.setdefault(message.get('author', 'unknown'), []).append(message.get('text', ''))

    metrics: dict[str, dict] = {}
    hedge_words = {'maybe', 'perhaps', 'likely', 'possibly', 'probably', 'might', 'could', 'not sure', 'i think', 'i guess'}
    knowledge_words = {'i know', 'i saw', 'i was', 'i did', 'i checked', 'i ran', 'i found'}
    time_words = {'yesterday', 'today', 'tonight', 'morning', 'afternoon', 'evening', 'at', 'before', 'after'}

    for author, texts in grouped.items():
        joined = ' '.join(texts)
        words = joined.split()
        sentences = max(1, sum(text.count('.') + text.count('?') + text.count('!') for text in texts))
        word_count = max(1, len(words))

        hedge_count = 0
        lowered = joined.lower()
        for phrase in hedge_words:
            hedge_count += lowered.count(phrase)

        knowledge_count = 0
        for phrase in knowledge_words:
            knowledge_count += lowered.count(phrase)

        time_count = sum(1 for w in words if w.lower().strip('.,') in time_words or re.match(r'\d{1,2}:\d{2}', w))
        entity_count = sum(1 for w in words if w[:1].isupper() or re.search(r'\d', w))
        self_refs = sum(1 for w in words if w.lower() in {'i', 'me', 'my', 'mine'})
        question_ratio = sum(text.count('?') for text in texts) / max(1, len(texts))

        metrics[author] = {
            'specificity_score': round(entity_count / max(1, sentences), 3),
            'hedge_density': round(hedge_count / word_count, 3),
            'self_reference_ratio': round(self_refs / word_count, 3),
            'knowledge_claim_ratio': round(knowledge_count / word_count, 3),
            'question_ratio': round(question_ratio, 3),
            'temporal_specificity': round(time_count / max(1, sentences), 3),
            'word_count': word_count,
            'hedge_count': hedge_count,
        }

    return metrics


def z_scores(metrics: dict[str, dict]) -> dict[str, dict]:
    keys = ['specificity_score', 'hedge_density', 'self_reference_ratio', 'knowledge_claim_ratio', 'question_ratio', 'temporal_specificity']
    scores: dict[str, dict] = {author: {} for author in metrics}
    for key in keys:
        values = [metrics[a][key] for a in metrics]
        mean = sum(values) / max(1, len(values))
        variance = sum((v - mean) ** 2 for v in values) / max(1, len(values))
        std = math.sqrt(variance) if variance > 0 else 1.0
        for author in metrics:
            scores[author][key] = round((metrics[author][key] - mean) / std, 2)
    return scores


def pick_flagged_author(zscore_map: dict[str, dict]) -> str | None:
    for author, scores in zscore_map.items():
        anomalies = sum(1 for value in scores.values() if abs(value) >= 1.5)
        if anomalies >= 2:
            return author
    return next(iter(zscore_map.keys()), None)
