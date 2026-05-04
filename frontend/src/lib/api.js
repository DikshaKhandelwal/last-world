const API_BASE = '';

export async function startSession() {
  const response = await fetch(`${API_BASE}/api/game/start`, { method: 'POST' });
  if (!response.ok) {
    throw new Error('Failed to start session');
  }
  return response.json();
}

export async function fetchGameState(sessionId) {
  const response = await fetch(`${API_BASE}/api/game/state/${sessionId}`);
  if (!response.ok) {
    throw new Error('Failed to load game state');
  }
  return response.json();
}

export async function submitLevelInput(sessionId, level, rawInput) {
  const response = await fetch(`${API_BASE}/api/game/level/${sessionId}/input`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ level, raw_input: rawInput }),
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || 'Failed to submit level input');
  }
  return response.json();
}

export async function submitDecision(sessionId, level, decisionType, value) {
  const response = await fetch(`${API_BASE}/api/human/${sessionId}/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ level, decision_type: decisionType, value }),
  });
  if (!response.ok) {
    throw new Error('Failed to submit decision');
  }
  return response.json();
}

export async function runNaive(prompt, system = '') {
  const response = await fetch(`${API_BASE}/api/pipeline/naive`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, system }),
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || 'Failed naive call');
  }
  return response.json();
}
