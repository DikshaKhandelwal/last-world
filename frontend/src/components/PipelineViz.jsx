import React from 'react';
import './PipelineViz.css';

export default function PipelineViz({ steps = [] }) {
  return (
    <div className="pipeline-shell">
      <div className="pipeline-title">Live inference pipeline</div>
      <div className="pipeline-grid">
        {steps.map((step) => (
          <div key={step.step_id} className={`pipeline-step ${step.status}`} data-status={step.status}>
            <div className="step-dot" />
            <div className="step-content">
              <span className="step-label">{step.label}</span>
              <span className="step-meta">{step.meta || step.output || step.reason || ''}</span>
              {step.retries > 0 && <div className="retry-counter">[RETRY {step.retries}]</div>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
