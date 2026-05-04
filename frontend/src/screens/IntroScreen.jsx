import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const INTRO_LINES = [
  { text: "May 14, 2041.", pauseAfter: 2000 },
  { text: "Global inference infrastructure:", append: { text: "COLLAPSE.", color: "var(--red)", delay: 400 }, pauseAfter: 1500 },
  { text: "Every frontier model.", nextLine: "Unreachable.", pauseAfter: 1500 },
  { text: "Banking systems.", nextLine: "Transportation grids.", nextLine2: "Legal arbitration.", nextLine3: "Medical diagnostics.", rapid: true, pauseAfter: 1500 },
  { text: "All dependent on inference.", nextLine: "All failing.", pauseAfter: 3000 },
  { text: "One model remains.", small: true, color: "var(--text-secondary)", pauseAfter: 1500 },
  { text: "Qwen 3.", append: { text: "0.6 Billion Parameters.", color: "var(--text-secondary)", size: "var(--text-lg)", delay: 800 }, pauseAfter: 3000 },
  { text: "You are the Systems Operator.", pauseAfter: 2000 },
  { text: "Five failures are incoming.", nextLine: "You will solve them.", nextLine2: "Together.", slowFadeNext2: true, pauseAfter: 2500 }
];

export default function IntroScreen({ onComplete }) {
  const [currentLineIndex, setCurrentLineIndex] = useState(0);
  const [showCollapse, setShowCollapse] = useState(false);
  const [showNext1, setShowNext1] = useState(false);
  const [showNext2, setShowNext2] = useState(false);
  const [showNext3, setShowNext3] = useState(false);
  const [showSubLine, setShowSubLine] = useState(false);
  const [isFlashing, setIsFlashing] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const audioRef = useRef(null);

  useEffect(() => {
    // Play background voice narration
    if (audioRef.current) {
      audioRef.current.volume = 0.6;
      audioRef.current.play().catch(err => console.log('Audio autoplay blocked:', err));
    }
  }, []);

  useEffect(() => {
    if (currentLineIndex >= INTRO_LINES.length) {
      setTimeout(() => {
        setIsFlashing(true);
        setTimeout(onComplete, 80); // White flash duration
      }, 1000);
      return;
    }

    const currentLine = INTRO_LINES[currentLineIndex];
    let timings = [];

    // Reset sub-states
    setShowCollapse(false);
    setShowNext1(false);
    setShowNext2(false);
    setShowNext3(false);
    setShowSubLine(false);

    // Schedule inner reveals
    if (currentLine.append) {
      timings.push(setTimeout(() => (currentLine.append.text === 'COLLAPSE.' ? setShowCollapse(true) : setShowSubLine(true)), currentLine.append.delay));
    }
    if (currentLine.nextLine) {
      timings.push(setTimeout(() => setShowNext1(true), currentLine.rapid ? 300 : 600));
    }
    if (currentLine.nextLine2) {
      timings.push(setTimeout(() => setShowNext2(true), currentLine.rapid ? 600 : 1200));
    }
    if (currentLine.nextLine3) {
      timings.push(setTimeout(() => setShowNext3(true), currentLine.rapid ? 900 : 1800));
    }

    // Schedule next main line
    const totalDuration = 800 + currentLine.pauseAfter + 600; // fade in + pause + active display time roughly
    const nextLineTimer = setTimeout(() => {
      setCurrentLineIndex(prev => prev + 1);
    }, totalDuration);
    
    timings.push(nextLineTimer);

    return () => timings.forEach(clearTimeout);
  }, [currentLineIndex, onComplete]);

  return (
    <>
      {/* Background Voice Audio */}
      <audio
        ref={audioRef}
        src="/audio/intro-narration.mp3"
        loop={false}
        muted={isMuted}
        style={{ display: 'none' }}
      />

      <div style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'var(--black)',
        fontFamily: 'var(--font-narrative)',
        color: 'var(--text-primary)',
        textAlign: 'center'
      }}>
        {/* Mute Button */}
        <button
          onClick={() => {
            setIsMuted(!isMuted);
            if (audioRef.current) {
              audioRef.current.muted = !isMuted;
            }
          }}
          style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            zIndex: 1000,
            backgroundColor: 'rgba(255,255,255,0.1)',
            border: '1px solid rgba(255,255,255,0.3)',
            color: 'var(--text-primary)',
            padding: '8px 12px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => e.target.style.backgroundColor = 'rgba(255,255,255,0.2)'}
          onMouseLeave={(e) => e.target.style.backgroundColor = 'rgba(255,255,255,0.1)'}
        >
          {isMuted ? '🔇 Unmute' : '🔊 Mute'}
        </button>
        <AnimatePresence mode='wait'>
          {currentLineIndex < INTRO_LINES.length && (
            <motion.div
              key={currentLineIndex}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.8, exit: { duration: 0.6 } }} // Spec: 800ms fade in, 600ms fade out
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '16px'
              }}
            >
              {renderLineContent(INTRO_LINES[currentLineIndex])}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Camera Cut Flash */}
      {isFlashing && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: '#fff',
          zIndex: 9999,
          animation: 'fadeOut 0.08s ease-out forwards'
        }} />
      )}
    </>
  );

  function renderLineContent(line) {
    const mainStyle = {
      fontSize: line.small ? 'var(--text-lg)' : 'var(--text-2xl)',
      color: line.color || 'var(--text-primary)'
    };

    return (
      <>
        <div style={mainStyle}>
          {line.text}
          {line.append && line.append.text === 'COLLAPSE.' && showCollapse && (
            <span style={{ color: line.append.color, marginLeft: '12px' }}>{line.append.text}</span>
          )}
        </div>
        
        {line.nextLine && showNext1 && (
          <motion.div initial={{opacity: 0}} animate={{opacity: 1}} transition={{duration: 0.5}} style={mainStyle}>{line.nextLine}</motion.div>
        )}
        
        {line.nextLine2 && showNext2 && (
          <motion.div initial={{opacity: 0}} animate={{opacity: 1}} transition={{duration: line.slowFadeNext2 ? 1.5 : 0.5}} style={mainStyle}>{line.nextLine2}</motion.div>
        )}
        
        {line.nextLine3 && showNext3 && (
          <motion.div initial={{opacity: 0}} animate={{opacity: 1}} transition={{duration: 0.5}} style={mainStyle}>{line.nextLine3}</motion.div>
        )}

        {line.append && line.append.text !== 'COLLAPSE.' && showSubLine && (
          <motion.div initial={{opacity: 0}} animate={{opacity: 1}} transition={{duration: 0.5}} style={{ color: line.append.color, fontSize: line.append.size, marginTop: '8px' }}>
            {line.append.text}
          </motion.div>
        )}
      </>
    );
  }
}
