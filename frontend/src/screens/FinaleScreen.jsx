import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import TypeWriter from '../components/TypeWriter';

export default function FinaleScreen({ onReturnToStandby }) {
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    const t1 = setTimeout(() => setPhase(1), 1800);
    const t2 = setTimeout(() => setPhase(2), 3600);
    const t3 = setTimeout(() => setPhase(3), 5600);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 1.2 }}
      style={{
        width: '100%',
        height: '100%',
        minHeight: '100vh',
        backgroundColor: 'var(--black)',
        backgroundImage:
          'radial-gradient(ellipse 80% 50% at 50% 20%, rgba(126, 240, 193, 0.12) 0%, transparent 55%), radial-gradient(ellipse 60% 40% at 50% 80%, rgba(242, 179, 90, 0.08) 0%, transparent 50%)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '48px 32px',
        boxSizing: 'border-box',
      }}
    >
      <div style={{ maxWidth: '640px', width: '100%', display: 'flex', flexDirection: 'column', gap: '28px' }}>
        <div style={{ fontFamily: 'var(--font-terminal)', fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', letterSpacing: 'var(--tracking-widest)' }}>
          SYSTEM FAILURE PROTOCOL // SESSION TERMINAL
        </div>

        <div style={{ color: 'var(--green-bright)', fontFamily: 'var(--font-terminal)', fontSize: 'clamp(var(--text-base), 2.5vw, var(--text-lg))' }}>
          <TypeWriter text="> PROTOCOL COMPLETE // ALL FIVE CRISES CLOSED" speed={28} />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: phase >= 1 ? 1 : 0, y: phase >= 1 ? 0 : 12 }}
          transition={{ duration: 0.7 }}
          style={{
            borderLeft: '1px solid var(--amber)',
            paddingLeft: '24px',
            fontFamily: 'var(--font-terminal)',
            fontSize: 'var(--text-sm)',
            color: 'var(--text-secondary)',
            lineHeight: 1.7,
            letterSpacing: '0.04em',
          }}
        >
          Dead code. Rigged arguments. Wrong voice. Corrupted data. Last translation.
          <br />
          <span style={{ color: 'var(--amber)' }}>Each arc ended in verifiable output.</span>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: phase >= 2 ? 1 : 0 }}
          transition={{ duration: 0.9 }}
          style={{
            fontFamily: 'var(--font-narrative)',
            fontSize: 'var(--text-xl)',
            color: 'var(--text-primary)',
            lineHeight: 1.65,
          }}
        >
          You ran the same small model twice: once naive, once inside the system. The gap between those columns was the whole story. Nothing left to simulate.
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: phase >= 3 ? 1 : 0 }}
          transition={{ duration: 0.8 }}
          style={{
            fontFamily: 'var(--font-terminal)',
            fontSize: 'var(--text-xs)',
            color: 'var(--text-dim)',
            letterSpacing: 'var(--tracking-widest)',
          }}
        >
          LOG SEALED // OPERATOR RELEASED // STANDBY
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: phase >= 3 ? 1 : 0 }}
          transition={{ duration: 0.5 }}
          style={{ marginTop: '24px' }}
        >
          <button
            type="button"
            onClick={onReturnToStandby}
            style={{
              background: 'transparent',
              border: '1px solid var(--green)',
              color: 'var(--green)',
              fontFamily: 'var(--font-terminal)',
              fontSize: 'var(--text-sm)',
              padding: '14px 28px',
              cursor: 'pointer',
              letterSpacing: 'var(--tracking-widest)',
              transition: 'border-color 0.2s, color 0.2s, box-shadow 0.2s',
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.boxShadow = '0 0 24px var(--green-glow)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            [ RETURN TO STANDBY ]
          </button>
        </motion.div>
      </div>
    </motion.div>
  );
}
