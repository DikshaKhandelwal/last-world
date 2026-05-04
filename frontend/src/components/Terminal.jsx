import React, { useEffect, useRef } from 'react';
import './Terminal.css';

export default function Terminal({ lines = [] }) {
  const terminalRef = useRef(null);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [lines]);

  return (
    <div className="terminal-container">
      <div className="terminal-header">
        <span>LAST MODEL: SYSTEM FAILURE PROTOCOL</span>
        <span className="terminal-status">DEGRADED</span>
      </div>
      <div className="terminal-body" ref={terminalRef}>
        {lines.map((line, index) => (
          <div key={`${line}-${index}`} className="terminal-line">
            {line}
          </div>
        ))}
        <div className="terminal-cursor">_</div>
      </div>
    </div>
  );
}
