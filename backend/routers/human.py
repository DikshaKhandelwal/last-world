from __future__ import annotations

from fastapi import APIRouter, HTTPException

from models.requests import HumanCorrectionRequest, HumanDecisionRequest, HumanEditorialRequest
from models.responses import DecisionResponse
from utils.session_store import get_session, update_session

router = APIRouter()


@router.post('/{session_id}/decision', response_model=DecisionResponse)
async def submit_decision(session_id: str, payload: HumanDecisionRequest):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail='Session not found')
    session.human_decision = payload.model_dump()
    session.awaiting_human = False
    session.human_event.set()
    update_session(session)
    return DecisionResponse(accepted=True, pipeline_resumed=True)


@router.post('/{session_id}/correction')
async def submit_correction(session_id: str, payload: HumanCorrectionRequest):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail='Session not found')
    session.human_decision = payload.model_dump()
    update_session(session)
    return {'accepted': True}


@router.post('/{session_id}/editorial')
async def submit_editorial(session_id: str, payload: HumanEditorialRequest):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail='Session not found')
    session.human_decision = payload.model_dump()
    update_session(session)
    return {'accepted': True, 'reprompt_triggered': not payload.passed}
