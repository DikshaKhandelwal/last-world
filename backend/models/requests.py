from pydantic import BaseModel


class GameStartRequest(BaseModel):
    pass


class LevelInputRequest(BaseModel):
    level: int
    raw_input: str


class NaiveCallRequest(BaseModel):
    prompt: str
    system: str | None = None


class CodeReviewRequest(BaseModel):
    session_id: str
    code: str
    language: str | None = 'python'


class ArgumentRequest(BaseModel):
    session_id: str
    text: str


class MessagesRequest(BaseModel):
    session_id: str
    messages: str


class CSVRequest(BaseModel):
    session_id: str
    csv_text: str


class SimplifyRequest(BaseModel):
    session_id: str
    text: str


class HumanDecisionRequest(BaseModel):
    level: int
    decision_type: str
    value: str | bool


class HumanCorrectionRequest(BaseModel):
    level: int
    row: int
    column: str
    action: str
    value: str | int | float | bool | None = None


class HumanEditorialRequest(BaseModel):
    level: int
    gate: str
    passed: bool
