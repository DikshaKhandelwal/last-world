"""
LEVEL 2 PIPELINE — THE RIGGED QUESTION
"""

from pipelines.base import BasePipeline
from processors.argument_analyzer import ArgumentAnalyzer
from inference.client import qwen_request


class Level2Pipeline(BasePipeline):
    """Logical fallacy detection pipeline."""

    async def run(self, text: str) -> dict:
        """Execute the fallacy detection pipeline."""
        
        # STEP 0: Naive Qwen output
        step_naive = self.add_step("naive_qwen", "Naive Qwen 0.6B")
        await self.step_start(step_naive)
        naive_output = await self._get_naive_output(text)
        await self.step_done(step_naive, naive_output[:100] + "...")

        # STEP 1: Argument analysis
        step_analysis = self.add_step("argument_analysis", "Analyze Argument Structure")
        await self.step_start(step_analysis)
        analyzer = ArgumentAnalyzer(text)
        analysis = analyzer.analyze()
        await self.step_done(step_analysis, f"Extracted {len(analysis['claims'])} claims")

        # STEP 2: Generate explanations for each fallacy
        step_explanations = self.add_step("fallacy_explanations", "Generate Explanations")
        await self.step_start(step_explanations)
        explanations = {}
        for fallacy in analysis.get("fallacies", []):
            explanation = await self._get_fallacy_explanation(fallacy, text)
            explanations[fallacy.fallacy_type.value] = explanation
        await self.step_done(step_explanations, f"Generated {len(explanations)} explanations")

        # Build proof panel
        proof_panel = {
            "naive_output": naive_output,
            "system_qwen_raw": "\n".join(explanations.values()) or "No model explanation generated.",
            "verified_output": [
                {
                    "type": f.fallacy_type.value,
                    "description": explanations.get(f.fallacy_type.value, f.description),
                    "claims": f.triggering_claims,
                    "severity": f.severity
                }
                for f in analysis.get("fallacies", [])
            ],
            "verification_line": "Read the highlighted claims in the original argument and confirm the evidence gap directly."
        }

        return {
            "success": True,
            "level": 2,
            "fallacies_found": len(analysis.get("fallacies", [])),
            "analysis": {
                "claims": [
                    {
                        "text": c.text,
                        "line_number": c.line_number,
                        "is_evidence": c.is_evidence,
                        "is_conclusion": c.is_conclusion,
                    }
                    for c in analysis.get("claims", [])
                ],
                "conclusion_idx": analysis.get("conclusion_idx"),
                "dependencies": analysis.get("dependencies"),
                "fallacies": [
                    {
                        "fallacy_type": f.fallacy_type.value,
                        "description": f.description,
                        "triggering_claims": f.triggering_claims,
                        "severity": f.severity,
                    }
                    for f in analysis.get("fallacies", [])
                ],
            },
            "explanations": explanations,
            "proof_panel": proof_panel,
            "events": await self._get_all_events()
        }

    async def _get_naive_output(self, text: str) -> str:
        """Get naive Qwen output."""
        prompt = f"""What logical fallacies are in this argument?

{text}

List the fallacies you see."""
        
        try:
            return await qwen_request(prompt, max_tokens=200)
        except Exception:
            return "[Error retrieving naive output]"

    async def _get_fallacy_explanation(self, fallacy, text: str) -> str:
        """Get specific explanation for a fallacy."""
        prompt = f"""This argument contains {fallacy.fallacy_type.value}.

Argument:
{text}

Explain specifically how this fallacy appears in the argument.
Keep it to one sentence under 20 words."""
        
        try:
            return await qwen_request(prompt, max_tokens=30)
        except Exception:
            return fallacy.description

    async def _get_all_events(self):
        """Get all emitted events."""
        events = []
        while not self._events.empty():
            events.append(await self._events.get())
        return events
