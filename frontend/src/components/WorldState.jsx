import React from 'react';
import './WorldState.css';

export default function WorldState({ worldState, sessionId, currentLevel, completedLevels = [] }) {
  return (
    <div className="world-state">
      <div className="world-title">Session status</div>
      <div className="world-grid">
        <div>
          <span className="world-label">Session</span>
          <strong>{sessionId ? sessionId.slice(0, 8) : '—'}</strong>
        </div>
        <div>
          <span className="world-label">Current level</span>
          <strong>{currentLevel}</strong>
        </div>
        <div>
          <span className="world-label">Score</span>
          <strong>{worldState?.percentage?.toFixed ? `${worldState.percentage.toFixed(0)}%` : '0%'}</strong>
        </div>
        <div>
          <span className="world-label">Completed</span>
          <strong>{completedLevels.length}/5</strong>
        </div>
      </div>
    </div>
  );
}
