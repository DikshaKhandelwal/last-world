import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import PipelineGraph from '../components/PipelineGraph';
import StruggleMeter from '../components/StruggleMeter';
import ProofPanel from '../components/ProofPanel';

export default function PipelineScreen({ level, inputData, sessionId, onComplete }) {
  const [nodes, setNodes] = useState([]);
  const [feed, setFeed] = useState([]);
  const [confidence, setConfidence] = useState(95);
  const [retries, setRetries] = useState(0);
  const [stats, setStats] = useState({ inferences: 0, completed: 0, total: 0, unresolved: 0 });
  const [isTyping, setIsTyping] = useState(false);
  const [result, setResult] = useState(null);
  const [phase, setPhase] = useState('running');
  const feedEndRef = useRef(null);

  // Auto-scroll feed
  useEffect(() => {
    feedEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [feed]);

  useEffect(() => {
    const addLog = (type, text) => {
      setFeed(prev => [...prev, { id: Date.now() + Math.random(), type, text }]);
    };

    const updateNode = (id, updates) => {
      setNodes(prev => prev.map(n => n.id === id ? { ...n, ...updates } : n));
    };

    const run = async () => {
      try {
        setIsTyping(true);
        addLog('SYSTEM', 'Running redesigned pipeline...');
        const endpointByLevel = {
          1: '/api/pipeline/level1/code_review',
          2: '/api/pipeline/level2/argument',
          3: '/api/pipeline/level3/messages',
          4: '/api/pipeline/level4/csv',
          5: '/api/pipeline/level5/simplify',
        };
        const payloadByLevel = {
          1: { session_id: sessionId, code: inputData, language: 'python' },
          2: { session_id: sessionId, text: inputData },
          3: { session_id: sessionId, messages: inputData },
          4: { session_id: sessionId, csv_text: inputData },
          5: { session_id: sessionId, text: inputData },
        };
        const response = await fetch(`http://localhost:8000${endpointByLevel[level]}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payloadByLevel[level]),
        });
        if (!response.ok) {
          throw new Error('Pipeline request failed');
        }
        const data = await response.json();
        addLog('MODEL_OUT', 'Pipeline finished. Rendering proof panel.');
        setResult(data);
        setNodes((data.events || []).filter((e) => e.event === 'step_start').map((e) => ({
          id: JSON.parse(e.data).step_id,
          label: JSON.parse(e.data).label,
          status: 'success',
          output: 'done',
          retries: 0,
        })));
        setStats((s) => ({ ...s, inferences: 5, completed: 5, total: 5 }));
        setIsTyping(false);
        setTimeout(() => setPhase('proof'), 1200);
      } catch (error) {
        addLog('RETRY', String(error));
        setConfidence((c) => Math.max(10, c - 20));
        setRetries((r) => r + 1);
        setIsTyping(false);
      }
    };

    run();
  }, [sessionId, level, onComplete, inputData]);

  return (
    <div style={{
      width: '100%', height: '100%',
      backgroundColor: 'var(--black)',
      display: 'flex',
      padding: '40px',
      gap: '40px'
    }}>
      {/* LEFT COLUMN: GRAPH */}
      <div style={{ width: '30%', display: 'flex', flexDirection: 'column' }}>
        <PipelineGraph nodes={nodes} />
      </div>

      {/* CENTER COLUMN: FEED */}
      <div style={{ width: '40%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ fontFamily: 'var(--font-terminal)', fontSize: 'var(--text-xs)', letterSpacing: 'var(--tracking-widest)', color: 'var(--text-secondary)', marginBottom: '16px' }}>
          LIVE SYSTEM OUTPUT
          <span style={{ display: 'inline-block', width: '6px', height: '1em', backgroundColor: 'var(--amber)', animation: 'blink 1s step-end infinite', marginLeft: '6px', verticalAlign: 'bottom' }} />
        </div>
        
        <div style={{
          flex: 1,
          backgroundColor: 'var(--deep)',
          border: '1px solid var(--border)',
          padding: '16px',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px'
        }}>
          <AnimatePresence>
            {feed.map((log) => (
              <LogLine key={log.id} log={log} />
            ))}
          </AnimatePresence>
          {isTyping && (
             <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ fontFamily: 'var(--font-terminal)', fontSize: 'var(--text-sm)', color: 'var(--text-primary)' }}>
               [MODEL] &gt; <span style={{ display: 'inline-block', width: '6px', height: '1em', backgroundColor: 'var(--text-primary)', animation: 'blink 0.5s step-end infinite', verticalAlign: 'bottom' }} />
             </motion.div>
          )}
          <div ref={feedEndRef} />
        </div>
      </div>

      {/* RIGHT COLUMN: STATS / PROOF */}
      <div style={{ width: '30%', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
        <StruggleMeter confidence={confidence} attempts={stats.inferences} retries={retries} stats={stats} />
        <div style={{ marginTop: '24px', flex: 1, minHeight: 0, overflowY: 'auto', paddingRight: '6px' }}>
        {phase === 'running' && (
          <div style={{ border: '1px solid var(--border)', padding: '12px', background: 'var(--deep)' }}>
            <div style={{ color: 'var(--amber)', fontSize: 'var(--text-xs)', marginBottom: '6px' }}>
              GENERATING RESULTS...
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-xs)' }}>
              Running naive baseline, system inference, and verification checks.
            </div>
          </div>
        )}
        {phase === 'proof' && result?.proof_panel && (
          <div>
            <ProofPanel proof={result.proof_panel} />
            <button
              onClick={() => onComplete(result)}
              style={{
                width: '100%',
                marginTop: '14px',
                background: 'transparent',
                border: '1px solid var(--green)',
                color: 'var(--green)',
                fontFamily: 'var(--font-terminal)',
                padding: '10px 12px',
                cursor: 'pointer'
              }}
            >
              CONTINUE
            </button>
          </div>
        )}
        </div>
      </div>
    </div>
  );
}

function LogLine({ log }) {
  const getColor = () => {
    switch(log.type) {
      case 'SYSTEM': return 'var(--text-secondary)';
      case 'MODEL': return 'var(--text-primary)';
      case 'MODEL_OUT': return 'var(--amber-bright)';
      case 'VALID': return 'var(--green)';
      case 'RETRY': return 'var(--red)';
      case 'HUMAN': return 'var(--amber)';
      default: return 'var(--text-primary)';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      style={{
        fontFamily: 'var(--font-terminal)',
        fontSize: 'var(--text-sm)',
        lineHeight: 1.6,
        color: getColor()
      }}
    >
      <span style={{ marginRight: '8px' }}>[{log.type}]</span>
      {log.text}
    </motion.div>
  );
}
