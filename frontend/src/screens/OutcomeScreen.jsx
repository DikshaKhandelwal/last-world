import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import TypeWriter from '../components/TypeWriter';

export default function OutcomeScreen({ success = true, isFinalCrisis = false, onContinue }) {
  const [phase, setPhase] = useState(0);

  // Time sequence
  useEffect(() => {
    const t1 = setTimeout(() => setPhase(1), 1500); // report card appears
    const t2 = setTimeout(() => setPhase(2), 2500); // narrative appears
    const t3 = setTimeout(() => setPhase(3), 4000); // continue prompt appears

    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };
  }, []);

  const bgGlow = success ? 'var(--green-glow)' : 'var(--red-glow)';
  const mainColor = success ? 'var(--green-bright)' : 'var(--red-bright)';
  const headerText = success ? '> OUTCOME: SUCCESS // CRISIS AVERTED' : '> OUTCOME: FAILURE // SYSTEM COMPROMISED';
  const continueText = !success
    ? '[ SYSTEM LOST. REBOOT? ]'
    : isFinalCrisis
      ? '[ CLOSE THE ARC // FINAL DEBRIEF › ]'
      : '[ CONTINUE TO NEXT CRISIS › ]';

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 1 }}
      style={{
        width: '100%',
        height: '100%',
        backgroundColor: 'var(--black)',
        backgroundImage: `radial-gradient(ellipse at center, ${bgGlow} 0%, transparent 60%)`,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: 'var(--font-terminal)'
      }}
    >
      <div style={{ maxWidth: '600px', width: '100%', display: 'flex', flexDirection: 'column', gap: '32px' }}>
        
        {/* HEADER */}
        <div style={{ color: mainColor, fontSize: 'var(--text-lg)' }}>
          <TypeWriter text={headerText} speed={30} />
        </div>

        {/* REPORT CARD */}
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: phase >= 1 ? 1 : 0, y: phase >= 1 ? 0 : 10 }}
          transition={{ duration: 0.6 }}
          style={{
            borderLeft: `1px solid ${mainColor}`,
            paddingLeft: '24px',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
          }}
        >
          <StatRow label="EXECUTION TIME" value="14.2s" color={success ? 'var(--green)' : 'var(--red)'} />
          <StatRow label="INFERENCES" value="003" color={success ? 'var(--green)' : 'var(--red)'} />
          <StatRow label="RETRIES" value="01" color={success ? 'var(--green)' : 'var(--red)'} />
          <StatRow label="FINAL CONFIDENCE" value={success ? '95%' : '14%'} color={success ? 'var(--green)' : 'var(--red)'} />
        </motion.div>

        {/* NARRATIVE */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: phase >= 2 ? 1 : 0 }}
          transition={{ duration: 1 }}
          style={{
            fontFamily: 'var(--font-narrative)',
            fontSize: 'var(--text-xl)',
            color: 'var(--text-primary)',
            lineHeight: 1.6,
            marginTop: '16px'
          }}
        >
          {success ? (
            "Cascade origin confirmed. Manual failover initiated. The grid stabilizes just as the automated SLA breach triggers were spinning up. It holds."
          ) : (
            "Incorrect origin confirmed. Failover applied to healthy systems. The cascade accelerates. Visibility lost across all remaining operational sectors."
          )}
        </motion.div>

        {/* CONTINUE BTN */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: phase >= 3 ? [1, 0.4, 1] : 0 }}
          transition={phase >= 3 ? { repeat: Infinity, duration: 2 } : { duration: 0.4 }}
          style={{ marginTop: '48px', alignSelf: 'flex-start' }}
        >
          <button
            onClick={phase >= 3 ? onContinue : undefined}
            style={{
              background: 'transparent',
              border: 'none',
              color: mainColor,
              fontFamily: 'var(--font-terminal)',
              fontSize: 'var(--text-sm)',
              cursor: phase >= 3 ? 'pointer' : 'default',
              padding: 0,
              letterSpacing: 'var(--tracking-widest)'
            }}
          >
            {continueText}
          </button>
        </motion.div>

      </div>
    </motion.div>
  );
}

function StatRow({ label, value, color }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--text-sm)' }}>
      <span style={{ color: 'var(--text-secondary)', letterSpacing: 'var(--tracking-widest)' }}>{label}</span>
      <span style={{ color }}>{value}</span>
    </div>
  );
}
