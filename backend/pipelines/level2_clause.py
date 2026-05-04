from __future__ import annotations

from inference.client import infer
from inference.validator import length_gated_infer, validated_infer_with_raw
from pipelines.base import BasePipeline
from processors.argument_processor import Claim, detect_fallacy, extract_claims_from_lines, pick_verification_line


class ClausePipeline(BasePipeline):
    async def run(self, argument_text: str) -> dict:
        if len(argument_text.split()) < 40:
            await self.emit('model_limit', {'message': 'Input too short. Minimum 40 words required.'})
            return {'status': 'limit_reached'}

        # Precompute naive output
        s0 = self.add_step('naive', 'Getting naive baseline')
        await self.step_start(s0)
        naive_output = await infer(f'What logical fallacies are in this argument?\n\n{argument_text[:1200]}')
        await self.step_done(s0, 'Baseline captured')

        s1 = self.add_step('claims', 'Extracting factual claims')
        await self.step_start(s1)
        claim_prompt = (
            'Read this argument. List every factual claim being made.\n'
            'Write each claim as a single short sentence.\n'
            'Format: one claim per line, starting with a dash.\n'
            'Do not interpret. Do not evaluate. Only extract.\n\n'
            f'{argument_text[:1200]}'
        )
        claim_raw = await infer(claim_prompt)
        claim_texts = extract_claims_from_lines(claim_raw)
        claims = [Claim(text=c) for c in claim_texts[:6]]
        await self.step_done(s1, f'Extracted {len(claims)} claims')

        s2 = self.add_step('evidence', 'Labeling evidence')
        await self.step_start(s2)
        system_output = claim_raw
        for claim in claims:
            verdict, _, _ = await validated_infer_with_raw(
                f'Is this claim supported by specific verifiable evidence in the original text? Answer EVIDENCED or ASSERTED.\nClaim: {claim.text}\n\nOriginal text:\n{argument_text[:1200]}',
                {'EVIDENCED', 'ASSERTED'},
                transform=lambda x: x.strip().split()[0].upper(),
            )
            claim.evidence = verdict
        await self.step_done(s2, 'Evidence labels assigned')

        s3 = self.add_step('match', 'Matching fallacy structure')
        await self.step_start(s3)
        fallacy = detect_fallacy(argument_text, claims)
        await self.step_done(s3, f'Fallacy: {fallacy}')

        s4 = self.add_step('explain', 'Generating plain-language explanation')
        await self.step_start(s4)
        explanation, _ = await length_gated_infer(
            f'The argument contains {fallacy}.\nClaims: {", ".join(c.text for c in claims)}\nComplete this sentence in under 20 words: "This is misleading because _______________"',
            max_words=20,
        )
        await self.step_done(s4, 'Explanation generated')

        verification_line = pick_verification_line(claims)
        verified_output = {
            'fallacy': fallacy,
            'claims': [{'text': c.text, 'evidence': c.evidence} for c in claims],
            'explanation': explanation,
        }

        await self.emit('pipeline_complete', {
            'level': 2,
            'proof_panel': {
                'naive_output': naive_output,
                'system_output': system_output,
                'verified_output': verified_output,
                'verification_line': verification_line,
            },
        })
        return {'status': 'complete', 'fallacy': fallacy, 'claims': verified_output['claims']}
