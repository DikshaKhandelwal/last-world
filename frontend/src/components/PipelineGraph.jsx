import React from 'react';
import PipelineNode from './PipelineNode';

export default function PipelineGraph({ nodes }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
      {nodes.map((node, index) => (
        <PipelineNode 
          key={index}
          label={node.label}
          status={node.status}
          output={node.output}
          retries={node.retries}
          isLast={index === nodes.length - 1}
        />
      ))}
    </div>
  );
}
