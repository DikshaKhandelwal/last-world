from __future__ import annotations

import asyncio
from collections import Counter

from inference.validator import validated_infer


async def majority_vote(prompt: str, whitelist: set[str], system: str = '', votes: int = 3) -> tuple[str, float]:
    tasks = [validated_infer(prompt, whitelist, system) for _ in range(votes)]
    results = await asyncio.gather(*tasks)
    outcomes = [result for result, _ in results]
    counts = Counter(outcomes)
    winner, winning_count = counts.most_common(1)[0]
    if winner == 'UNRESOLVED' or winning_count < (votes // 2 + 1):
        return 'UNRESOLVED', 0.0
    return winner, winning_count / votes
