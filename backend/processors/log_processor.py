from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from dateutil import parser as dateparser


def deduplicate_logs(raw_logs: str) -> str:
    lines = raw_logs.strip().split('\n')
    counts = Counter(lines)
    seen = set()
    result = []
    for line in lines:
        if line in seen:
            continue
        seen.add(line)
        count = counts[line]
        if count > 3:
            result.append(f'[repeated {count}x] {line}')
        else:
            result.extend([line] * count)
    return '\n'.join(result)


def extract_timestamps(logs: str) -> list[dict]:
    patterns = [
        r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}',
        r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}',
        r'\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}',
    ]
    results = []
    for i, line in enumerate(logs.split('\n')):
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    ts = dateparser.parse(match.group(), fuzzy=True)
                    results.append({'timestamp': ts, 'line': line, 'index': i})
                    break
                except Exception:
                    continue
    return sorted(results, key=lambda x: x['timestamp'] or datetime.min)


def isolate_anomalies(logs: str, max_lines: int = 8) -> list[str]:
    lines = [line for line in logs.split('\n') if line.strip()]
    error_keywords = [
        'error', 'fatal', 'critical', 'exception', 'fail', 'refused',
        'timeout', 'panic', 'crash', 'killed', 'oom', 'segfault', 'abort',
    ]
    anomalies = [line for line in lines if any(kw in line.lower() for kw in error_keywords)]
    if not anomalies:
        anomalies = lines[-max_lines:]
    return anomalies[:max_lines]
