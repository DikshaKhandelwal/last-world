"""
LEVEL 4 PIPELINE — THE CORRUPTED ORACLE
Data forensics pipeline.
"""

import io
import pandas as pd
from pipelines.base import BasePipeline
from processors.data_profiler import profile_dataframe, detect_impossible_combos, infer_column_domain
from inference.client import qwen_request


class Level4Pipeline(BasePipeline):
    async def run(self, csv_text: str) -> dict:
        # STEP 0: naive model output
        step_naive = self.add_step('naive_qwen', 'Naive Qwen 0.6B')
        await self.step_start(step_naive)
        naive = await self._get_naive_output(csv_text)
        await self.step_done(step_naive, naive[:120] + '...')

        # STEP 1: parse CSV
        step_parse = self.add_step('parse_csv', 'Parse & Profile Data')
        await self.step_start(step_parse)
        try:
            df = pd.read_csv(io.StringIO(csv_text))
            profile = profile_dataframe(df)
            combos = detect_impossible_combos(df)
            await self.step_done(step_parse, f'Profiled {len(df)} rows, {len(profile)} cols')
        except Exception as e:
            await self.step_done(step_parse, f'Failed to parse CSV: {str(e)}')
            return {'success': False, 'error': 'parse_failed'}

        # STEP 2: model domain inference for suspicious columns
        step_model = self.add_step('domain_infer', 'Model Domain Inference')
        await self.step_start(step_model)
        domain_infers = {}
        for col, meta in profile.items():
            if col == '_meta':
                continue
            try:
                domain = infer_column_domain(col, df[col])
            except Exception:
                domain = 'unknown'
            # Ask model to hypothesize domain based on sample
            sample = df[col].dropna().astype(str).head(20).tolist()
            prompt = f"""Column name: {col}\nSample values: {sample}\nWhat domain or meaning does this column likely represent? One short phrase."""
            try:
                resp = await qwen_request(prompt, max_tokens=30)
            except Exception:
                resp = domain
            domain_infers[col] = resp.strip()
            await self.emit('domain_infer', {'column': col, 'domain': resp})
        await self.step_done(step_model, f'Inferred domains for {len(domain_infers)} cols')

        # STEP 3: impact ranking (simple: number of issues per column)
        step_rank = self.add_step('impact_rank', 'Rank Impact')
        await self.step_start(step_rank)
        impact = []
        for col, meta in profile.items():
            if col == '_meta':
                continue
            issues_count = len(meta.get('suspicious_values', [])) + len([c for c in combos if c.get('issue') and c.get('row') is not None and c.get('issue').startswith(col)])
            impact.append({'column': col, 'issues': issues_count})
        impact_sorted = sorted(impact, key=lambda x: x['issues'], reverse=True)
        await self.step_done(step_rank, f'Ranked {len(impact_sorted)} columns')

        proof_panel = {
            'naive_output': naive,
            'system_qwen_raw': "\n".join([f"{k}: {v}" for k, v in domain_infers.items()]),
            'verified_output': {
                'profile': profile,
                'impossible_combos': combos,
                'domain_inference': domain_infers,
                'impact_rank': impact_sorted
            },
            'verification_line': (
                f"Look at row {combos[0].get('row')} in your dataset and verify the impossible value."
                if combos else
                "Inspect the highest ranked anomaly in the profile table."
            )
        }

        return {
            'success': True,
            'level': 4,
            'proof_panel': proof_panel,
            'events': await self._get_all_events()
        }

    async def _get_naive_output(self, text: str) -> str:
        prompt = f"""Find data quality issues in this CSV (first 200 chars):\n{text[:200]}"""
        try:
            return await qwen_request(prompt, max_tokens=150)
        except Exception:
            return '[error retrieving naive output]'

    async def _get_all_events(self):
        events = []
        while not self._events.empty():
            events.append(await self._events.get())
        return events
