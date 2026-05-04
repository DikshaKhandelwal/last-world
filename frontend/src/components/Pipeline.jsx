import React from 'react';
import './Pipeline.css';

export default function Pipeline({ nodes }) {
  return (
    <div className="pipeline-section">
      <h3>Inference Pipeline</h3>
      <div className="pipeline">
        {nodes.map((node, idx) => (
          <div
            key={idx}
            className={`node ${node.status}`}
            title={node.status}
          >
            <div className="node-name">{node.name}</div>
            <div className="node-status">
              {node.status === 'pending' && '○'}
              {node.status === 'executing' && '◐'}
              {node.status === 'retry' && '⚠'}
              {node.status === 'success' && '✓'}
              {node.status === 'failed' && '✗'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
