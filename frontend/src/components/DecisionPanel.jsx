import React from 'react';
import './DecisionPanel.css';

export default function DecisionPanel({ prompt, options = [], onDecide }) {
  if (!prompt) {
    return null;
  }

  return (
    <div className="decision-panel">
      <div className="decision-title">Human judgment required</div>
      <p>{prompt}</p>
      <div className="decision-actions">
        {options.map((option) => (
          <button key={option} className="decision-btn" onClick={() => onDecide(option)}>
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}
