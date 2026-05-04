from __future__ import annotations

from inference.client import infer
from inference.validator import length_gated_infer
from pipelines.base import BasePipeline
from processors.behavioral_processor import compute_author_metrics, parse_messages, pick_flagged_author, z_scores


class HollowPipeline(BasePipeline):
    async def run(self, raw_messages: str) -> dict:
        # Precompute naive output
        s0 = self.add_step('naive', 'Getting naive baseline')
        await self.step_start(s0)
        naive_output = await infer(f'Who in these messages is being suspicious?\n\n{raw_messages[:1200]}')
        await self.step_done(s0, 'Baseline captured')

        s1 = self.add_step('parse', 'Parsing attributed messages')
        await self.step_start(s1)
        messages = parse_messages(raw_messages)
        await self.step_done(s1, f'Parsed {len(messages)} messages')
        if not messages:
            await self.step_failed(s1)
            await self.emit('pipeline_complete', {
                'level': 3,
                'proof_panel': {
                    'naive_output': naive_output,
                    'system_output': '',
                    'verified_output': {'error': 'No messages parsed'},
                    'verification_line': 'Provide at least two attributed lines (Name: message).',
                },
            })
            return {'status': 'no_messages'}

        s2 = self.add_step('metrics', 'Extracting behavioral metrics')
        await self.step_start(s2)
        metrics = compute_author_metrics(messages)
        zscore_map = z_scores(metrics)
        await self.step_done(s2, f'Computed metrics for {len(metrics)} authors')

        s3 = self.add_step('flag', 'Flagging outliers')
        await self.step_start(s3)
        suspect = pick_flagged_author(zscore_map) or 'unknown'
        await self.step_done(s3, f'Flagged {suspect}')

        s4 = self.add_step('explain', 'Explaining evasive topic')
        await self.step_start(s4)
        system_output = ''
        if suspect in metrics:
            hedges = metrics[suspect]['hedge_count']
            prompt = (
                f"Author {suspect} uses {hedges} hedge words. "
                f"Complete this sentence in under 20 words: 'They are most evasive when talking about _______________'."
            )
            system_output = await infer(prompt)
        explanation, _ = await length_gated_infer(
            f"Rewrite this in under 20 words: {system_output}",
            max_words=20,
        )
        await self.step_done(s4, 'Explanation generated')

        verification_line = 'Count hedge words in the flagged author message. Target shown in metrics.'
        verified_output = {
            'suspect': suspect,
            'metrics': metrics,
            'z_scores': zscore_map,
            'explanation': explanation,
        }

        await self.emit('pipeline_complete', {
            'level': 3,
            'proof_panel': {
                'naive_output': naive_output,
                'system_output': system_output,
                'verified_output': verified_output,
                'verification_line': verification_line,
            },
        })
        return {'status': 'complete', 'suspect': suspect}
