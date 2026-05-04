def calculate_survival_score(session) -> dict:
    results = session.level_results
    if not results:
        return {
            'score': 0,
            'total': 5,
            'percentage': 0,
            'total_inferences': session.total_inferences,
            'total_retries': session.total_retries,
            'summary': [],
        }

    score = sum(1 for r in results if r.outcome == 'success')
    partial = sum(0.5 for r in results if r.outcome == 'partial')
    total_score = score + partial

    return {
        'score': total_score,
        'survival_score': total_score,
        'total': 5,
        'percentage': (total_score / 5) * 100,
        'total_inferences': session.total_inferences,
        'total_retries': session.total_retries,
        'total_human_decisions': sum(len(r.human_decisions) for r in results),
        'estimated_cost_usd': round(session.total_inferences * 0.000003, 6),
        'summary': [
            {'level': r.level, 'outcome': r.outcome}
            for r in results
        ],
    }
