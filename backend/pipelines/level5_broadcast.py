from __future__ import annotations

from inference.client import infer
from inference.validator import length_gated_infer
from pipelines.base import BasePipeline
from processors.text_processor import extract_numbers, readability_score, validate_facts, word_count


class BroadcastPipeline(BasePipeline):
    async def run(self, draft_text: str) -> dict:
        # Precompute naive output
        s0 = self.add_step('naive', 'Getting naive baseline')
        await self.step_start(s0)
        naive_output = await infer(
            'Rewrite this for a general audience in under 100 words at a Grade 6 reading level.\n\n' + draft_text[:1500]
        )
        await self.step_done(s0, 'Baseline captured')

        s1 = self.add_step('facts', 'Extracting facts')
        await self.step_start(s1)
        fact_prompt = (
            'Read this technical text. List every specific fact: numbers, names, events, causes, times.\n'
            'One fact per line. Start each with a dash. Keep each under 15 words.\n\n'
            f'{draft_text[:1500]}'
        )
        system_output = await infer(fact_prompt)
        facts = [line[1:].strip() for line in system_output.split('\n') if line.strip().startswith('-')]
        await self.step_done(s1, f'Extracted {len(facts)} facts')

        s2 = self.add_step('draft', 'Generating broadcast draft')
        await self.step_start(s2)
        draft, attempts = await length_gated_infer(
            'Write a public announcement using ONLY these facts. Under 100 words. No technical terms.\n\n' + '\n'.join(facts[:8]),
            max_words=100,
        )
        if attempts > 1:
            await self.step_retry(s2, 'Draft exceeded word limit')
        await self.step_done(s2, f'{word_count(draft)} words')

        s3 = self.add_step('verify', 'Verifying readability and facts')
        await self.step_start(s3)
        readability = readability_score(draft)
        unsupported = validate_facts(draft, facts)
        original_numbers = extract_numbers(draft_text)
        preserved_numbers = [num for num in original_numbers if num in draft]
        await self.step_done(s3, f'Grade {readability["grade_level"]}, facts preserved {len(preserved_numbers)}/{len(original_numbers)}')

        verification_line = 'Check that key numbers from the original appear in the draft, then verify the word count under 100.'
        verified_output = {
            'draft': draft,
            'readability': readability,
            'unsupported_sentences': unsupported,
            'facts_preserved': f'{len(preserved_numbers)}/{len(original_numbers)}',
        }

        await self.emit('pipeline_complete', {
            'level': 5,
            'proof_panel': {
                'naive_output': naive_output,
                'system_output': system_output,
                'verified_output': verified_output,
                'verification_line': verification_line,
            },
        })
        return {'status': 'complete', 'draft': draft}
