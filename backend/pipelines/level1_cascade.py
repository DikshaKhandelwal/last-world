from __future__ import annotations

import logging

from inference.client import infer
from inference.validator import length_gated_infer
from pipelines.base import BasePipeline
from processors.code_processor import detect_code_flags, pick_verification_line

logger = logging.getLogger(__name__)


class CascadePipeline(BasePipeline):
    async def run(self, raw_code: str) -> dict:
        if len(raw_code.split('\n')) > 400:
            await self.emit('model_limit', {'message': 'INPUT TOO LONG — limit to 400 lines.'})
            return {'status': 'limit_reached'}

        # Precompute naive output
        s0 = self.add_step('naive', 'Getting naive baseline')
        await self.step_start(s0)
        naive_output = await infer(f'Review this code for bugs:\n\n{raw_code[:1200]}')
        await self.step_done(s0, 'Baseline captured')

        s1 = self.add_step('parse', 'Parsing code')
        await self.step_start(s1)
        lines = raw_code.split('\n')
        await self.step_done(s1, f'Loaded {len(lines)} lines')

        s2 = self.add_step('flags', 'Matching bug patterns')
        await self.step_start(s2)
        flags = detect_code_flags(raw_code)
        if not flags:
            await self.step_failed(s2)
            await self.emit('pipeline_complete', {
                'level': 1,
                'proof_panel': {
                    'naive_output': naive_output,
                    'system_output': '',
                    'verified_output': {'flags': [], 'summary': 'No flags detected'},
                    'verification_line': 'No issues detected. Provide a longer snippet if you expected a bug.',
                },
            })
            return {'status': 'no_flags'}
        await self.step_done(s2, f'Flagged {len(flags)} suspicious patterns')

        s3 = self.add_step('explain', 'Explaining failure conditions')
        await self.step_start(s3)
        explanations = []
        system_output = None
        for index, flag in enumerate(flags, start=1):
            await self.step_update(s3, f'{index}/{len(flags)} analyzing line {flag.line_number}')
            prompt = (
                f'Given this code fragment:\n{flag.fragment}\n\n'
                f'A reviewer flagged this as potentially {flag.flag_type}.\n'
                "Complete this sentence in under 15 words: 'This breaks when ______________'"
            )
            raw = await infer(prompt)
            if system_output is None:
                system_output = raw
            sentence, _ = await length_gated_infer(
                f"Rewrite this response to be under 15 words and start with a verb: {raw}",
                max_words=15,
            )
            explanations.append({
                'flag_type': flag.flag_type,
                'line': flag.line_number,
                'fragment': flag.fragment,
                'explanation': sentence,
            })
        await self.step_done(s3, f'Generated {len(explanations)} explanations')

        verification_line = pick_verification_line(flags)
        verified_output = {
            'flags': [e for e in explanations],
            'summary': f'{len(explanations)} potential issues flagged',
        }

        await self.emit('pipeline_complete', {
            'level': 1,
            'proof_panel': {
                'naive_output': naive_output,
                'system_output': system_output or '',
                'verified_output': verified_output,
                'verification_line': verification_line,
            },
        })
        return {'status': 'complete', 'flags': explanations}
