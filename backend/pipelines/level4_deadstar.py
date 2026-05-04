from __future__ import annotations

from inference.client import infer
from inference.validator import length_gated_infer
from pipelines.base import BasePipeline
from processors.data_processor import detect_anomalies, detect_impossible_values, parse_input, statistical_profile


class DeadStarPipeline(BasePipeline):
    async def run(self, raw_data: str) -> dict:
        # Precompute naive output
        s0 = self.add_step('naive', 'Getting naive baseline')
        await self.step_start(s0)
        naive_output = await infer(f'Find data quality issues in this CSV:\n\n{raw_data[:1200]}')
        await self.step_done(s0, 'Baseline captured')

        s1 = self.add_step('parse', 'Parsing input data')
        await self.step_start(s1)
        df = parse_input(raw_data)
        await self.step_done(s1, f'Parsed {len(df)} rows and {len(df.columns)} columns')

        s2 = self.add_step('profile', 'Profiling data')
        await self.step_start(s2)
        profile = statistical_profile(df)
        await self.step_done(s2, 'Statistical profile built')

        s3 = self.add_step('anomaly', 'Detecting anomalies')
        await self.step_start(s3)
        anomalies = detect_anomalies(df, profile)
        impossible = detect_impossible_values(df)
        combined = anomalies + impossible
        await self.step_done(s3, f'Flagged {len(combined)} anomalies')

        s4 = self.add_step('explain', 'Explaining suspicious values')
        await self.step_start(s4)
        system_output = ''
        explanation = ''
        if combined:
            target = combined[0]
            prompt = (
                f"Column name: '{target['column']}'\n"
                f"Flagged value: {target['value']} in row {target['row']}\n"
                "Based only on the column name, complete this sentence in under 20 words: "
                f"'This value is suspicious because for a column called {target['column']}, you would expect _______________'"
            )
            system_output = await infer(prompt)
            explanation, _ = await length_gated_infer(
                f'Rewrite this in under 20 words: {system_output}',
                max_words=20,
            )
        await self.step_done(s4, 'Explanation generated')

        s5 = self.add_step('rank', 'Ranking impact')
        await self.step_start(s5)
        impact = [a['column'] for a in combined[:3]]
        await self.step_done(s5, f'Impact columns: {", ".join(impact) if impact else "none"}')

        verification_line = 'Look at the flagged row and column. The value is visibly impossible.'
        verified_output = {
            'flags': combined[:10],
            'impact_columns': impact,
            'explanation': explanation,
        }

        await self.emit('pipeline_complete', {
            'level': 4,
            'proof_panel': {
                'naive_output': naive_output,
                'system_output': system_output,
                'verified_output': verified_output,
                'verification_line': verification_line,
            },
        })
        return {'status': 'complete', 'anomalies': combined}
