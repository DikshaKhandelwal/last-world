import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LEVELS } from '../lib/constants';

export default function InputScreen({ level = 1, sessionId, onComplete }) {
  const [data, setData] = useState('');
  const [isCompiling, setIsCompiling] = useState(false);
  const currentCrisis = LEVELS[level - 1];
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => {
      setData(evt.target.result);
    };
    reader.readAsText(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => {
      setData(evt.target.result);
    };
    reader.readAsText(file);
  };

  const handleSubmit = async () => {
    if (data.length < 10 || isCompiling) return;
    
    setIsCompiling(true);
    try {
      if (sessionId) {
        await fetch(`http://localhost:8000/api/game/level/${sessionId}/input`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ level, raw_input: data })
        });
      }
      setTimeout(() => {
        onComplete(data);
      }, 800);
    } catch (e) {
      console.error(e);
      setIsCompiling(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.6 }}
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: 'var(--black)',
        fontFamily: 'var(--font-terminal)'
      }}
    >
      {/* ZONE 1 — HEADER */}
      <div style={{
        height: '80px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '0 40px',
        borderBottom: '1px solid var(--border)',
        flexShrink: 0
      }}>
        <div style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)', letterSpacing: 'var(--tracking-widest)' }}>
          INPUTTING DATA — CRISIS 0{level}
        </div>
        <div style={{ color: 'var(--amber)', fontSize: 'var(--text-sm)', display: 'flex', alignItems: 'center' }}>
          [WAITING FOR OPERATOR]
          <span style={{ 
            display: 'inline-block', 
            width: '8px', 
            height: '1em', 
            backgroundColor: 'var(--amber)', 
            animation: 'blink 1s step-end infinite',
            marginLeft: '8px'
          }} />
        </div>
      </div>

      {/* ZONE 2 — INPUT AREA */}
      <div 
        style={{ flexGrow: 1, position: 'relative', overflow: 'hidden' }}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
      >
        <textarea
          ref={textareaRef}
          value={data}
          onChange={(e) => setData(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isCompiling}
          placeholder="> PASTE DATA TO BEGIN ANALYSIS_ OR DRAG AND DROP FILE HERE_"
          autoFocus
          style={{
            width: '100%',
            height: '100%',
            backgroundColor: 'transparent',
            border: 'none',
            outline: 'none',
            resize: 'none',
            padding: '40px',
            fontFamily: 'var(--font-terminal)',
            fontSize: 'var(--text-base)',
            color: isCompiling ? 'var(--text-muted)' : 'var(--text-primary)',
            lineHeight: 1.5,
            transition: 'color 0.4s ease'
          }}
        />
        {!data && (
          <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', pointerEvents: 'none' }}>
             <label style={{ 
               color: 'var(--text-secondary)', 
               border: '1px dashed var(--text-secondary)', 
               padding: '12px 24px', 
               cursor: 'pointer', 
               pointerEvents: 'auto',
               fontFamily: 'var(--font-terminal)',
               fontSize: 'var(--text-sm)',
               letterSpacing: 'var(--tracking-widest)',
               transition: 'all 0.2s',
               display: 'inline-block',
               background: 'var(--black)'
             }}
             onMouseOver={(e) => { e.target.style.color = 'var(--text-primary)'; e.target.style.borderColor = 'var(--text-primary)'; }}
             onMouseOut={(e) => { e.target.style.color = 'var(--text-secondary)'; e.target.style.borderColor = 'var(--text-secondary)'; }}
             >
                UPLOAD PAYLOAD
                <input type="file" id="file-uploader" style={{ display: 'none' }} onChange={handleFileUpload} />
             </label>
          </div>
        )}
      </div>

      {/* ZONE 3 — ACTION BAR */}
      <AnimatePresence>
        {data.length > 50 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.3 }}
            style={{
              height: '60px',
              borderTop: '1px solid var(--border)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '0 40px',
              flexShrink: 0,
              backgroundColor: 'var(--black)'
            }}
          >
            <div style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-xs)' }}>
              CHARACTERS: {data.length} | EST TOKENS: {Math.floor(data.length / 4)}
            </div>
            
            <button
              onClick={handleSubmit}
              disabled={isCompiling}
              style={{
                background: isCompiling ? 'var(--border-lit)' : 'transparent',
                border: '1px solid var(--amber)',
                color: isCompiling ? 'var(--text-secondary)' : 'var(--amber)',
                padding: '8px 16px',
                fontFamily: 'var(--font-terminal)',
                fontSize: 'var(--text-sm)',
                cursor: isCompiling ? 'default' : 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              {isCompiling ? '[COMPILING DATA...]' : '[INITIATE PIPELINE ↵]'}
            </button>
          </motion.div>
        )}
      </AnimatePresence>

    </motion.div>
  );
}
