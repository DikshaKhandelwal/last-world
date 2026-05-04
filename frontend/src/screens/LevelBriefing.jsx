import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { LEVELS } from '../lib/constants';
import TypeWriter from '../components/TypeWriter';

export default function LevelBriefing({ level = 1, onEnterMission }) {
  const [linesRevealed, setLinesRevealed] = useState(0);
  const currentCrisis = LEVELS[level - 1];

  const handleLineComplete = useCallback(() => {
    setLinesRevealed(prev => prev + 1);
  }, []);

  return (
    <div style={{
      width: '100%',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      padding: '64px',
      position: 'relative'
    }}>
      
      {/* 2 Column Split Layout */}
      <div style={{ flex: 1, display: 'flex', gap: '64px' }}>
        
        {/* LEFT COLUMN: Narrative */}
        <motion.div 
          initial={{ opacity: 0, x: -40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, ease: [0.19, 1, 0.22, 1] }}
          style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
        >
          <div style={{
            fontFamily: 'var(--font-display)',
            fontSize: 'var(--text-xl)',
            color: 'var(--text-primary)',
            letterSpacing: 'var(--tracking-wide)',
            marginBottom: '8px'
          }}>
            CLASSIFIED BRIEFING
          </div>
          <div style={{
            color: 'var(--amber)',
            fontFamily: 'var(--font-terminal)',
            fontSize: 'var(--text-sm)',
            letterSpacing: 'max(0.24em, 2px)',
            marginBottom: '32px'
          }}>
            ━━━━━━━━━━━━
          </div>
          
          <div style={{ 
            fontFamily: 'var(--font-narrative)', 
            fontSize: 'var(--text-lg)',
            lineHeight: 1.6,
            color: 'var(--text-primary)',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px'
          }}>
            {currentCrisis.narrative.map((text, idx) => (
              <div key={idx} style={{ minHeight: '1.6em' }}>
                 {linesRevealed >= idx && (
                    <TypeWriter 
                      text={text} 
                      speed={idx === currentCrisis.narrative.length - 1 ? 40 : 20}
                      onComplete={handleLineComplete}
                      style={idx === currentCrisis.narrative.length - 1 ? { color: 'var(--text-secondary)' } : {}}
                    />
                 )}
              </div>
            ))}
          </div>
        </motion.div>

        {/* VERTICAL DIVIDER */}
        <motion.div 
          initial={{ scaleY: 0 }}
          animate={{ scaleY: 1 }}
          transition={{ duration: 0.8, ease: "circOut" }}
          style={{ width: '1px', backgroundColor: 'var(--border-lit)', transformOrigin: 'top' }} 
        />

        {/* RIGHT COLUMN: Mission Parameters */}
        <motion.div 
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, ease: [0.19, 1, 0.22, 1] }}
          style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
        >
          <div style={{
            fontFamily: 'var(--font-terminal)',
            fontSize: 'var(--text-sm)',
            color: 'var(--text-secondary)',
            letterSpacing: 'var(--tracking-widest)',
            marginBottom: '48px'
          }}>
            CRISIS {level} // {currentCrisis.name}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <ParamBlock label="LOCATION" value={`${currentCrisis.location.name} (${currentCrisis.location.lat}°, ${currentCrisis.location.lon}°)`} delay={0.15} />
            <ParamBlock label="SYSTEM" value={currentCrisis.system} delay={0.3} />
            <ParamBlock label="DOMAIN" value={currentCrisis.domain} delay={0.45} />
            <ParamBlock label="PRIORITY" value={currentCrisis.priority} delay={0.6} />
            <ParamBlock label="EST. IMPACT" value={currentCrisis.impact} color="var(--amber)" delay={0.75} />
          </div>
        </motion.div>
      </div>

      {/* BOTTOM BAR */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1, duration: 0.6 }}
        style={{
          borderTop: '1px solid var(--border-lit)',
          paddingTop: '24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        <div style={{ fontFamily: 'var(--font-terminal)', fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>
          <span style={{ color: 'var(--amber)' }}>[WARNING]</span> Model capability: MINIMAL
        </div>

        <button 
          onClick={onEnterMission}
          style={{
            background: 'transparent',
            border: '1px solid var(--border-lit)',
            color: 'var(--text-primary)',
            padding: '12px 24px',
            fontFamily: 'var(--font-terminal)',
            fontSize: 'var(--text-sm)',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            letterSpacing: 'var(--tracking-wider)'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.borderColor = 'var(--text-primary)';
            e.currentTarget.style.color = '#fff';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.borderColor = 'var(--border-lit)';
            e.currentTarget.style.color = 'var(--text-primary)';
          }}
        >
          [ENTER MISSION ›]
        </button>
      </motion.div>
    </div>
  );
}

function ParamBlock({ label, value, color = 'var(--text-primary)', delay }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay, duration: 0.5 }}
      style={{
        borderLeft: '1px solid var(--border)',
        paddingLeft: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '4px'
      }}
    >
      <div style={{ fontFamily: 'var(--font-terminal)', fontSize: 'var(--text-xs)', letterSpacing: 'var(--tracking-widest)', color: 'var(--text-secondary)' }}>
        {label}
      </div>
      <div style={{ fontFamily: 'var(--font-terminal)', fontSize: 'var(--text-base)', color }}>
        {value}
      </div>
    </motion.div>
  );
}
