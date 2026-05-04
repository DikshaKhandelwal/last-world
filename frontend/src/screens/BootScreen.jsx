import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import TypeWriter from '../components/TypeWriter';

const PHASE = {
  SYSTEM_ID: 'SYSTEM_ID',
  CONNECTIVITY: 'CONNECTIVITY',
  LOCAL_MODEL: 'LOCAL_MODEL',
  READY: 'READY',
  EXITING: 'EXITING'
};

const checks = [
  { text: '> CONNECTING TO INFERENCE CLUSTER', status: '[TIMEOUT]', type: 'error' },
  { text: '> CONNECTING TO BACKUP CLUSTER', status: '[TIMEOUT]', type: 'error' },
  { text: '> CONNECTING TO EDGE NODES', status: '[TIMEOUT]', type: 'error' },
  { text: '> SCANNING LOCAL FILESYSTEM', status: '[SCANNING]', type: 'scanning' }
];

const foundText = [
  "> qwen3:0.6b — 619M PARAMETERS",
  "> STATUS: OPERATIONAL (DEGRADED)",
  "> CONFIDENCE: LOW"
];

export default function BootScreen({ onComplete }) {
  const [phase, setPhase] = useState(PHASE.SYSTEM_ID);
  const [checkIndex, setCheckIndex] = useState(-1);
  const [foundIndex, setFoundIndex] = useState(-1);
  const [showFinalLine, setShowFinalLine] = useState(false);

  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.key === 'Enter' && phase === PHASE.READY) {
        setPhase(PHASE.EXITING);
        setTimeout(onComplete, 600);
      }
    };
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [phase, onComplete]);

  // Phase Orchestration
  useEffect(() => {
    if (phase === PHASE.SYSTEM_ID) {
      setTimeout(() => setPhase(PHASE.CONNECTIVITY), 2000);
    } else if (phase === PHASE.CONNECTIVITY) {
      if (checkIndex < checks.length) {
        setTimeout(() => setCheckIndex(prev => prev + 1), checkIndex === -1 ? 500 : 500);
      } else {
        setTimeout(() => setPhase(PHASE.LOCAL_MODEL), 400);
      }
    } else if (phase === PHASE.LOCAL_MODEL) {
      if (foundIndex < foundText.length) {
        setTimeout(() => setFoundIndex(prev => prev + 1), foundIndex === -1 ? 500 : 200);
      } else if (!showFinalLine) {
        setTimeout(() => setShowFinalLine(true), 200);
      } else {
        setTimeout(() => setPhase(PHASE.READY), 600);
      }
    }
  }, [phase, checkIndex, foundIndex, showFinalLine]);

  return (
    <motion.div 
      initial={{ opacity: 1 }}
      animate={{ opacity: phase === PHASE.EXITING ? 0 : 1 }}
      transition={{ duration: 0.6, ease: [0.77, 0, 0.175, 1] }}
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'left' // text aligned left inside centered container
      }}
    >
      <div style={{ maxWidth: '800px', width: '100%', padding: '0 40px' }}>
        
        {/* PHASE 1 */}
        {phase !== PHASE.EXITING && (
          <motion.div 
            animate={{ opacity: phase !== PHASE.SYSTEM_ID ? 0.3 : 1 }}
            transition={{ duration: 0.4 }}
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'var(--text-xl)',
              color: 'var(--text-secondary)',
              letterSpacing: 'var(--tracking-widest)',
              marginBottom: '32px'
            }}
          >
            <TypeWriter text="SYSTEM FAILURE PROTOCOL — v0.6B" speed={40} />
          </motion.div>
        )}

        {/* PHASE 2 */}
        {(phase === PHASE.CONNECTIVITY || phase === PHASE.LOCAL_MODEL || phase === PHASE.READY) && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontFamily: 'var(--font-terminal)', fontSize: 'var(--text-base)', marginBottom: '32px' }}>
            {checks.map((item, idx) => (
              idx <= checkIndex && (
                <div key={idx} style={{ display: 'flex' }}>
                  <TypeWriter text={item.text.padEnd(48, '.')} speed={15} />
                  <motion.span 
                    initial={item.type === 'error' ? { color: 'var(--red-bright)', opacity: 0 } : { opacity: 0 }}
                    animate={item.type === 'error' ? { color: 'var(--red)', opacity: 1 } : { opacity: [1, 0.5, 1] }}
                    transition={item.type === 'scanning' ? { repeat: Infinity, duration: 1.5 } : { duration: 0.3 }}
                    style={{ color: item.type === 'scanning' ? 'var(--amber)' : 'var(--red)' }}
                  >
                    &nbsp;{item.status}
                  </motion.span>
                </div>
              )
            ))}
          </div>
        )}

        {/* PHASE 3 */}
        {(phase === PHASE.LOCAL_MODEL || phase === PHASE.READY) && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontFamily: 'var(--font-terminal)', fontSize: 'var(--text-base)', marginBottom: '32px' }}>
            <motion.div style={{ color: 'var(--green-bright)', marginBottom: '8px' }}>
              <TypeWriter text="> LOCAL MODEL DETECTED" speed={10} />
            </motion.div>
            
            {foundText.map((text, idx) => (
              idx <= foundIndex && (
                <div key={idx} style={{ color: 'var(--text-secondary)' }}>
                   {text}
                </div>
              )
            ))}

            {showFinalLine && (
              <div style={{ marginTop: '16px', color: 'var(--text-primary)' }}>
                <TypeWriter text="> THIS IS ALL THAT REMAINS." speed={50} />
              </div>
            )}
          </div>
        )}

        {/* PHASE 4 */}
        {phase === PHASE.READY && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ fontFamily: 'var(--font-terminal)', fontSize: 'var(--text-base)', color: 'var(--amber)', marginTop: '24px' }}
          >
            &gt; PRESS ENTER TO BEGIN OPERATOR SESSION
            <span style={{ 
              display: 'inline-block', 
              width: '10px', 
              height: '1em', 
              backgroundColor: 'var(--amber)', 
              animation: 'blink 1s step-end infinite',
              verticalAlign: 'bottom'
            }} />
          </motion.div>
        )}

      </div>
    </motion.div>
  );
}
