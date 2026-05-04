from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from models.requests import LevelInputRequest
from models.responses import InputResponse, StartResponse
from pipelines.level1_cascade import CascadePipeline
from pipelines.level2_clause import ClausePipeline
from pipelines.level3_hollow import HollowPipeline
from pipelines.level4_deadstar import DeadStarPipeline
from pipelines.level5_broadcast import BroadcastPipeline
from utils.scoring import calculate_survival_score
from utils.session_store import attach_pipeline, create_session, get_session, update_session, LevelResult

router = APIRouter()

logger = logging.getLogger(__name__)


PIPELINES = {
    1: CascadePipeline,
    2: ClausePipeline,
    3: HollowPipeline,
    4: DeadStarPipeline,
    5: BroadcastPipeline,
}


async def _run_pipeline(session_id: str, level: int, raw_input: str, pipeline):
    session = get_session(session_id)
    if session is None:
        return

    result: dict[str, Any] = await pipeline.run(raw_input)
    outcome = 'partial' if result.get('status') == 'awaiting_human' else 'success'
    session = get_session(session_id)
    if session is None:
        return
    session.completed_levels.append(level)
    session.current_level = min(5, level + 1)
    session.level_results.append(LevelResult(level=level, outcome=outcome, payload=result))
    session.world_state.update(calculate_survival_score(session))
    session.total_inferences += result.get('inferences', 0)
    update_session(session)


@router.post('/start', response_model=StartResponse)
async def start_game():
    logger.info('start_game requested')
    session = create_session()
    logger.info('start_game created session_id=%s level=%s', session.session_id, session.current_level)
    return StartResponse(session_id=session.session_id, current_level=session.current_level, world_state=session.world_state)


@router.get('/state/{session_id}')
async def game_state(session_id: str):
    session = get_session(session_id)
    if session is None:
        logger.warning('game_state missing session_id=%s', session_id)
        raise HTTPException(status_code=404, detail='Session not found')
    session.world_state.update(calculate_survival_score(session))
    update_session(session)
    return {
        'session_id': session.session_id,
        'current_level': session.current_level,
        'world_state': session.world_state,
        'completed_levels': session.completed_levels,
        'survival_score': session.world_state.get('survival_score', 0),
        'total_inferences': session.total_inferences,
        'total_retries': session.total_retries,
        'awaiting_human': session.awaiting_human,
    }


@router.post('/level/{session_id}/input', response_model=InputResponse)
async def submit_level_input(session_id: str, payload: LevelInputRequest):
    session = get_session(session_id)
    if session is None:
        logger.warning('submit_level_input missing session_id=%s level=%s', session_id, payload.level)
        raise HTTPException(status_code=404, detail='Session not found')
    if payload.level not in PIPELINES:
        logger.warning('submit_level_input invalid level=%s session_id=%s', payload.level, session_id)
        raise HTTPException(status_code=400, detail='Invalid level')
    if len(payload.raw_input.strip()) < 10:
        logger.info('submit_level_input rejected short input session_id=%s level=%s', session_id, payload.level)
        return InputResponse(accepted=False, message='Input too short')

    session.current_level = payload.level
    pipeline_cls = PIPELINES[payload.level]
    pipeline = pipeline_cls(session_id)
    attach_pipeline(session_id, pipeline)
    update_session(session)
    logger.info('submit_level_input accepted session_id=%s level=%s', session_id, payload.level)
    asyncio.create_task(_run_pipeline(session_id, payload.level, payload.raw_input, pipeline))
    return InputResponse(accepted=True, message='Pipeline started')
