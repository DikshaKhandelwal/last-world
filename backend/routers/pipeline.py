from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from utils.session_store import get_session
from models.requests import NaiveCallRequest
from inference.client import infer
from pipelines.level1_dead_code import Level1Pipeline
from pipelines.level2_rigged_question import Level2Pipeline
from pipelines.level3_wrong_person import Level3Pipeline
from pipelines.level4_corrupted_oracle import Level4Pipeline
from pipelines.level5_last_translation import Level5Pipeline
from models.requests import CodeReviewRequest, ArgumentRequest, MessagesRequest, CSVRequest, SimplifyRequest

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get('/{session_id}/stream')
async def stream_pipeline(session_id: str):
    session = get_session(session_id)
    if session is None or session.pipeline is None:
        logger.warning('stream_pipeline missing session or pipeline session_id=%s', session_id)
        raise HTTPException(status_code=404, detail='Pipeline not found')
    logger.info('stream_pipeline connected session_id=%s', session_id)
    return StreamingResponse(session.pipeline.stream_events(), media_type='text/event-stream')


@router.post('/naive')
async def naive_call(payload: NaiveCallRequest):
    if not payload or not payload.prompt:
        raise HTTPException(status_code=400, detail='Missing prompt')
    try:
        raw = await infer(payload.prompt, system=payload.system or '')
        return {'raw': raw}
    except Exception as e:
        logger.exception('naive_call failed')
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/level1/code_review')
async def level1_code_review(payload: CodeReviewRequest):
    pipeline = Level1Pipeline(payload.session_id)
    result = await pipeline.run(payload.code, payload.language or 'python')
    return result


@router.post('/level2/argument')
async def level2_argument(payload: ArgumentRequest):
    pipeline = Level2Pipeline(payload.session_id)
    result = await pipeline.run(payload.text)
    return result


@router.post('/level3/messages')
async def level3_messages(payload: MessagesRequest):
    pipeline = Level3Pipeline(payload.session_id)
    result = await pipeline.run(payload.messages)
    return result


@router.post('/level4/csv')
async def level4_csv(payload: CSVRequest):
    pipeline = Level4Pipeline(payload.session_id)
    result = await pipeline.run(payload.csv_text)
    return result


@router.post('/level5/simplify')
async def level5_simplify(payload: SimplifyRequest):
    pipeline = Level5Pipeline(payload.session_id)
    result = await pipeline.run(payload.text)
    return result
