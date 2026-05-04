"""
LEVEL 1 — THE DEAD CODE
Static code analysis pipeline to find real bugs in user code.
"""

import asyncio
import json
from typing import Optional
from pipelines.base import BasePipeline, PipelineStep
from processors.code_analyzer import CodeAnalyzer, validate_bug_description
from inference.client import qwen_request


class Level1Pipeline(BasePipeline):
    """Code review pipeline using AST analysis + model inference."""

    def __init__(self, session_id: str):
        super().__init__(session_id)
        self.code_input = None
        self.language = None
        self.flags = []
        self.naive_output = None
        self.system_descriptions = {}
        self.proof_panel = {}

    async def run(self, code: str, language: str = "python") -> dict:
        """Execute the full Level 1 pipeline."""
        self.code_input = code
        self.language = language

        # STEP 0: Get naive model output (for proof panel)
        step_naive = self.add_step("naive_qwen", "Naive Qwen 0.6B")
        await self.step_start(step_naive)
        self.naive_output = await self._get_naive_output(code)
        await self.step_done(step_naive, self.naive_output[:100] + "...")

        # STEP 1: Static analysis
        step_analysis = self.add_step("static_analysis", "AST & Pattern Analysis")
        await self.step_start(step_analysis)
        analyzer = CodeAnalyzer(code, language)
        self.flags = analyzer.analyze()
        await self.step_done(step_analysis, f"Found {len(self.flags)} potential issues")

        # STEP 2: Model descriptions for each flag
        step_descriptions = self.add_step("model_descriptions", "Generate Descriptions")
        await self.step_start(step_descriptions)
        for i, flag in enumerate(self.flags):
            description = await self._get_bug_description(flag)
            if validate_bug_description(description, flag.bug_type):
                self.system_descriptions[i] = description
            await self.emit('description_generated', {'flag': i, 'description': description})
        await self.step_done(step_descriptions, f"Validated {len(self.system_descriptions)} descriptions")

        # STEP 3: Build proof panel
        self.proof_panel = {
            "naive_output": self.naive_output,
            "system_qwen_raw": "\n".join(self.system_descriptions.values()) or "No model descriptions generated.",
            "verified_output": [
                {
                    "bug_type": f.bug_type.value,
                    "line": f.line_number,
                    "severity": f.severity,
                    "code": f.code_fragment,
                    "description": self.system_descriptions.get(i, f.description),
                }
                for i, f in enumerate(self.flags)
            ],
            "verification_line": (
                f"Check line {self.flags[0].line_number} in your code; the failure condition is present there."
                if self.flags
                else "No deterministic bug flags found in this snippet."
            ),
        }

        return {
            "success": True,
            "level": 1,
            "bugs_found": len(self.flags),
            "flags": [
                {
                    "bug_type": f.bug_type.value,
                    "line_number": f.line_number,
                    "code_fragment": f.code_fragment,
                    "severity": f.severity,
                    "description": f.description,
                }
                for f in self.flags
            ],
            "descriptions": self.system_descriptions,
            "proof_panel": self.proof_panel,
            "events": await self._get_all_events()
        }

    async def _get_naive_output(self, code: str) -> str:
        """Get naive Qwen output for comparison."""
        prompt = f"""Review this code for bugs:

{code[:500]}

What bugs do you see?"""
        
        try:
            response = await qwen_request(prompt, max_tokens=150)
            return response
        except Exception as e:
            return f"[Error: {str(e)}]"

    async def _get_bug_description(self, flag) -> str:
        """Get model's specific description of the bug."""
        prompt = f"""The following code has a {flag.bug_type.value} bug:

{flag.code_fragment}

Describe specifically what fails and under what condition, in one sentence.
Start with a verb like "breaks", "fails", "crashes", or "returns".
Keep it under 20 words."""

        try:
            response = await qwen_request(prompt, max_tokens=30)
            return response.strip()
        except Exception as e:
            return f"Bug: {flag.bug_type.value}"

    async def _get_all_events(self):
        """Retrieve all emitted events."""
        events = []
        while not self._events.empty():
            events.append(await self._events.get())
        return events
