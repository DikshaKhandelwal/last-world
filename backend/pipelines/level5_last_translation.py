"""
LEVEL 5 PIPELINE — THE LAST TRANSLATION
Simplify technical text while preserving factual accuracy and reading level.
"""

from pipelines.base import BasePipeline
from inference.client import qwen_request
from processors.text_processor import readability_score, word_count, extract_numbers


class Level5Pipeline(BasePipeline):
    async def run(self, technical_text: str) -> dict:
        # STEP 0: naive model output
        step_naive = self.add_step('naive_qwen', 'Naive Qwen 0.6B')
        await self.step_start(step_naive)
        naive = await self._get_naive_output(technical_text)
        await self.step_done(step_naive, naive[:120] + '...')

        # STEP 1: Fact extraction (model constrained list)
        step_facts = self.add_step('fact_extraction', 'Fact Extraction')
        await self.step_start(step_facts)
        fact_prompt = f"""List the core facts in the following technical text as short bullets (one fact per line):\n\n{technical_text}\n\nOnly list facts and numbers, do not add commentary."""
        try:
            facts_raw = await qwen_request(fact_prompt, max_tokens=200)
        except Exception:
            facts_raw = ""
        facts = [line.strip('- ').strip() for line in facts_raw.split('\n') if line.strip()]
        original_numbers = extract_numbers(technical_text)
        await self.step_done(step_facts, f'Extracted {len(facts)} facts')

        # STEP 2: Term simplification (model per term)
        step_terms = self.add_step('term_simplification', 'Term Simplification')
        await self.step_start(step_terms)
        simplified_terms = {}
        # Extract candidate terms from text (camelCase, PascalCase, technical words)
        terms = set()
        for word in technical_text.split():
            w = word.strip(".,()[]{}:;\"'")
            if len(w) > 5 and w.isalpha():
                terms.add(w)
        for term in list(terms)[:30]:
            prompt = f"""Simplify this technical term into plain language (one short phrase): {term}"""
            try:
                resp = await qwen_request(prompt, max_tokens=10)
            except Exception:
                resp = term
            simplified_terms[term] = resp.strip()
            await self.emit('term_simplified', {'term': term, 'simple': resp})
        await self.step_done(step_terms, f'Simplified {len(simplified_terms)} terms')

        # STEP 3: Draft assembly (model structured template)
        step_draft = self.add_step('draft_assembly', 'Draft Simplified Text')
        await self.step_start(step_draft)
        draft_prompt = f"""Using these facts:\n{facts}\n\nAnd these simplified terms mapping:\n{simplified_terms}\n\nWrite a single-paragraph explanation under 100 words at grade 6 reading level. Be factual."""
        try:
            draft = await qwen_request(draft_prompt, max_tokens=200)
        except Exception:
            draft = ''
        await self.step_done(step_draft, f'Draft length {len(draft.split())} words')

        # STEP 4: Fact fidelity check (model binary per sentence)
        step_check = self.add_step('fidelity_check', 'Fact Fidelity Check')
        await self.step_start(step_check)
        sentences = [s.strip() for s in draft.split('.') if s.strip()]
        fidelity = {}
        for i, s in enumerate(sentences):
            prompt = f"""Is this sentence factually supported by the facts list?\nFacts:\n{facts}\n\nSentence:\n{s}\n\nAnswer YES or NO and a short reason."""
            try:
                resp = await qwen_request(prompt, max_tokens=40)
            except Exception:
                resp = 'NO: check failed'
            fidelity[i] = resp.strip()
            await self.emit('fidelity', {'sentence': i, 'result': resp})
        await self.step_done(step_check, f'Checked {len(sentences)} sentences')

        # STEP 5: Reading level verification
        step_level = self.add_step('reading_level', 'Reading Level Verification')
        await self.step_start(step_level)
        score = readability_score(draft)
        reading_level = score.get('grade_level', 0)
        final_word_count = word_count(draft)
        await self.step_done(step_level, f'Estimated grade {reading_level}')

        proof_panel = {
            'naive_output': naive,
            'system_qwen_raw': facts_raw,
            'verified_output': {
                'facts': facts,
                'simplified_terms': simplified_terms,
                'draft': draft,
                'fidelity': fidelity,
                'reading_level': reading_level,
                'word_count': final_word_count,
                'numbers_preserved': [n for n in original_numbers if n in draft.replace(',', '')],
            },
            'verification_line': 'Confirm key numbers are preserved and the final text stays under 100 words.'
        }

        return {
            'success': True,
            'level': 5,
            'proof_panel': proof_panel,
            'events': await self._get_all_events()
        }

    async def _get_naive_output(self, text: str) -> str:
        prompt = f"""Simplify this text to under 100 words:\n\n{text[:300]}"""
        try:
            return await qwen_request(prompt, max_tokens=150)
        except Exception:
            return '[error retrieving naive output]'

    async def _get_all_events(self):
        events = []
        while not self._events.empty():
            events.append(await self._events.get())
        return events
