from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class LevelResult:
    level: int
    outcome: str
    inferences: int = 0
    retries: int = 0
    human_decisions: list[dict[str, Any]] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class GameSession:
    session_id: str
    started_at: datetime
    current_level: int = 1
    completed_levels: list[int] = field(default_factory=list)
    level_results: list[LevelResult] = field(default_factory=list)
    pipeline: Any = None
    awaiting_human: bool = False
    human_event: asyncio.Event = field(default_factory=asyncio.Event)
    human_decision: dict[str, Any] | None = None
    total_inferences: int = 0
    total_retries: int = 0
    world_state: dict[str, Any] = field(default_factory=lambda: {
        'survival_score': 0,
        'status': 'operational',
        'threat_level': 'elevated',
    })


_sessions: dict[str, GameSession] = {}


def create_session() -> GameSession:
    sid = str(uuid.uuid4())
    session = GameSession(session_id=sid, started_at=datetime.utcnow())
    _sessions[sid] = session
    return session


def get_session(session_id: str) -> GameSession | None:
    return _sessions.get(session_id)


def update_session(session: GameSession) -> None:
    _sessions[session.session_id] = session


def attach_pipeline(session_id: str, pipeline: Any) -> GameSession:
    session = get_session(session_id)
    if session is None:
        raise KeyError(session_id)
    session.pipeline = pipeline
    update_session(session)
    return session
