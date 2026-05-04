"""
LEVEL 3 PIPELINE — THE WRONG PERSON
"""

from pipelines.base import BasePipeline
from processors.behavioral_analyzer import BehavioralAnalyzer
from inference.client import qwen_request


class Level3Pipeline(BasePipeline):
    async def run(self, messages_text: str) -> dict:
        # Naive model output
        step_naive = self.add_step("naive_qwen", "Naive Qwen 0.6B")
        await self.step_start(step_naive)
        naive = await self._get_naive_output(messages_text)
        await self.step_done(step_naive, naive[:120] + "...")

        # Behavioral analysis
        step_analysis = self.add_step("behavioral_analysis", "Linguistic Feature Extraction")
        await self.step_start(step_analysis)
        analyzer = BehavioralAnalyzer(messages_text)
        analysis = analyzer.analyze()
        await self.step_done(step_analysis, f"Analyzed {len(analysis.get('messages', {}))} authors")

        # Model task: for each flagged author, ask model what topic is being hedged
        step_model = self.add_step("model_topics", "Model Semantic Labels")
        await self.step_start(step_model)
        topics = {}
        for anomaly in analysis.get('anomalies', []):
            author = anomaly['author']
            prompt = f"""Author {author} has high hedge usage and anomalous patterns.

Messages:
{messages_text}

Identify the topic(s) the author is hedging about, in one short phrase."""
            try:
                resp = await qwen_request(prompt, max_tokens=30)
            except Exception:
                resp = "[failed to get topic]"
            topics[author] = resp.strip()
            await self.emit('topic_identified', {'author': author, 'topic': resp})
        await self.step_done(step_model, f"Identified topics for {len(topics)} authors")

        proof_panel = {
            'naive_output': naive,
            'system_qwen_raw': "\n".join([f"{author}: {topic}" for author, topic in topics.items()]) or "No anomalies required model labeling.",
            'verified_output': {
                'scores': analysis.get('scores'),
                'anomalies': analysis.get('anomalies'),
                'topics': topics
            },
            'verification_line': "Count hedge words in the flagged author message and compare to the group average."
        }

        return {
            'success': True,
            'level': 3,
            'analysis': analysis,
            'topics': topics,
            'proof_panel': proof_panel,
            'events': await self._get_all_events()
        }

    async def _get_naive_output(self, text: str) -> str:
        prompt = f"""Who is suspicious in these messages?

{text}

Explain briefly."""
        try:
            return await qwen_request(prompt, max_tokens=150)
        except Exception:
            return "[error retrieving naive output]"

    async def _get_all_events(self):
        events = []
        while not self._events.empty():
            events.append(await self._events.get())
        return events
