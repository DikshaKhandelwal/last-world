import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function StruggleMeter({ confidence, attempts, retries, stats }) {
  let color = 'var(--green)';
  let isPulsing = false;

  if (confidence <= 40) {
    color = 'var(--red)';
    if (confidence <= 10) isPulsing = true;
  } else if (confidence <= 70) {
    color = 'var(--amber)';
  }

  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - ((stats.completed / Math.max(1, stats.total)) * circumference);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px', width: '100%' }}>
      
      {/* Meter Bar Section */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div style={{ fontFamily: 'var(--font-terminal)', fontSize: 'var(--text-xs)', letterSpacing: 'var(--tracking-widest)', color: 'var(--text-secondary)' }}>
          MODEL CONFIDENCE
        </div>
        
        <div style={{ width: '100%', height: '4px', backgroundColor: 'var(--surface-2)', position: 'relative', overflow: 'hidden' }}>
          <motion.div 
            animate={{ width: `${confidence}%`, backgroundColor: color }}
            transition={{ duration: 0.6 }}
            style={{ position: 'absolute', top: 0, left: 0, height: '100%' }}
          />
        </div>
        
        <motion.div 
          animate={isPulsing ? { opacity: [1, 0.4, 1] } : { opacity: 1 }}
          transition={isPulsing ? { repeat: Infinity, duration: 0.6 } : {}}
          style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-xl)', color }}
        >
          {confidence}%
        </motion.div>
      </div>

      {/* Stats Section */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <StatLine label="INFERENCES" value={stats.inferences.toString().padStart(3, '0')} updateTrigger={stats.inferences} />
        <StatLine label="RETRIES" value={retries.toString().padStart(2, '0')} updateTrigger={retries} />
        <StatLine label="UNRESOLVED" value={stats.unresolved.toString()} updateTrigger={stats.unresolved} />
      </div>

      {/* Progress Arc */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '32px', gap: '16px' }}>
        <div style={{ position: 'relative', width: '90px', height: '90px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <svg width="90" height="90" style={{ transform: 'rotate(-90deg)', position: 'absolute', top: 0, left: 0 }}>
            {/* Background Arc */}
            <circle cx="45" cy="45" r={radius} stroke="var(--border)" strokeWidth="4" fill="none" />
            {/* Animated Fill Arc */}
            <motion.circle 
              cx="45" cy="45" r={radius} 
              stroke="var(--green)" strokeWidth="4" fill="none"
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              style={{ strokeDasharray: circumference }}
            />
          </svg>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-lg)', color: 'var(--text-primary)', zIndex: 1 }}>
            {stats.completed}/{stats.total}
          </div>
        </div>
        <div style={{ fontFamily: 'var(--font-terminal)', fontSize: 'var(--text-xs)', letterSpacing: 'var(--tracking-widest)', color: 'var(--text-secondary)' }}>
          STEPS COMPLETE
        </div>
      </div>

    </div>
  );
}

function StatLine({ label, value, updateTrigger }) {
  const [flash, setFlash] = useState(false);

  useEffect(() => {
    setFlash(true);
    const t = setTimeout(() => setFlash(false), 100);
    return () => clearTimeout(t);
  }, [updateTrigger]);

  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--font-terminal)', fontSize: 'var(--text-xs)' }}>
      <span style={{ color: 'var(--text-secondary)', letterSpacing: 'var(--tracking-widest)' }}>{label}</span>
      <span style={{ color: flash ? 'var(--amber)' : 'var(--text-primary)', transition: 'color 0.1s' }}>[{value}]</span>
    </div>
  );
}
