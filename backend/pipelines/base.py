from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncGenerator

from utils.session_store import get_session, update_session


class PipelineStep:
    def __init__(self, step_id: str, label: str):
        self.step_id = step_id
        self.label = label
        self.status = 'pending'
        self.retries = 0
        self.output = None


class BasePipeline:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.steps: list[PipelineStep] = []
        self._events: asyncio.Queue = asyncio.Queue()
        self._session = get_session(session_id)

    def add_step(self, step_id: str, label: str) -> PipelineStep:
        step = PipelineStep(step_id, label)
        self.steps.append(step)
        return step

    async def emit(self, event_type: str, data: dict):
        await self._events.put({'event': event_type, 'data': json.dumps(data)})

    async def step_start(self, step: PipelineStep):
        step.status = 'running'
        await self.emit('step_start', {'step_id': step.step_id, 'label': step.label})

    async def step_retry(self, step: PipelineStep, reason: str):
        step.retries += 1
        step.status = 'retry'
        if self._session:
            self._session.total_retries += 1
            update_session(self._session)
        await self.emit('step_retry', {'step_id': step.step_id, 'attempt': step.retries + 1, 'reason': reason})

    async def step_done(self, step: PipelineStep, output: Any):
        step.status = 'success'
        step.output = output
        await self.emit('step_done', {'step_id': step.step_id, 'output': str(output)[:200]})

    async def step_update(self, step: PipelineStep, output: Any):
        step.output = output
        await self.emit('step_update', {'step_id': step.step_id, 'output': str(output)[:200]})

    async def step_failed(self, step: PipelineStep):
        step.status = 'failed'
        await self.emit('step_failed', {'step_id': step.step_id, 'message': 'Model could not resolve. Human input required.'})

    async def human_required(self, prompt: str, options: list[str]):
        session = get_session(self.session_id)
        if session:
            session.awaiting_human = True
            session.human_event.clear()
            update_session(session)
        await self.emit('human_required', {'prompt': prompt, 'options': options})
        if session:
            await session.human_event.wait()
            session.awaiting_human = False
            update_session(session)

    async def stream_events(self) -> AsyncGenerator[str, None]:
        while True:
            event = await self._events.get()
            yield f"event: {event['event']}\ndata: {event['data']}\n\n"
            if event['event'] == 'pipeline_complete':
                break
