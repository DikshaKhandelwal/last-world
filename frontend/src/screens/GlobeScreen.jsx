import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import GlobeCanvas from '../components/GlobeCanvas';
import { LEVELS } from '../lib/constants';

export default function GlobeScreen({ level = 1, onComplete }) {
  const currentCrisis = LEVELS[level - 1];
  const [locked, setLocked] = useState(false);
  const [exiting, setExiting] = useState(false);

  const handleRotated = () => {
    setLocked(true);
  };

  useEffect(() => {
    if (locked) {
      const timer = setTimeout(() => {
        setExiting(true);
        setTimeout(onComplete, 800);
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [locked, onComplete]);

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: exiting ? 0 : 1 }}
      transition={{ duration: 0.8 }}
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative'
      }}
    >
      <div style={{ position: 'absolute', top: '15vh' }}>
        <motion.div
          animate={{ opacity: [1, 0] }}
          transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
          style={{
            fontFamily: 'var(--font-terminal)',
            fontSize: 'var(--text-sm)',
            letterSpacing: 'var(--tracking-widest)',
            color: 'var(--text-secondary)'
          }}
        >
          LOCATING CRISIS ORIGIN...
        </motion.div>
      </div>

      <motion.div 
        initial={{ scale: 0.3 }}
        animate={{ scale: exiting ? 1.4 : 1 }}
        transition={{ duration: 1.2, ease: [0.19, 1, 0.22, 1] }} // --ease-out-expo
        style={{ zIndex: 1 }}
      >
        <GlobeCanvas currentLevel={level} onRotated={handleRotated} />
      </motion.div>

      <div style={{ position: 'absolute', bottom: '20vh', display: 'flex', flexDirection: 'column', alignItems: 'center', zIndex: 2 }}>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: locked ? 1 : 0 }}
          transition={{ duration: 0.5 }}
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: 'var(--text-xl)',
            color: 'var(--text-primary)',
            marginBottom: '16px'
          }}
        >
          CRISIS {level} OF 5 — {currentCrisis?.name}
        </motion.div>
        
        {locked && (
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: '100%' }}
            transition={{ duration: 1 }}
            style={{ overflow: 'hidden', whiteSpace: 'nowrap' }}
          >
            <span style={{
              fontFamily: 'var(--font-terminal)',
              fontSize: 'var(--text-sm)',
              color: 'var(--amber)'
            }}>
              &gt; COORDINATES LOCKED — INITIATING BRIEFING
            </span>
          </motion.div>
        )}
      </div>

    </motion.div>
  );
}
