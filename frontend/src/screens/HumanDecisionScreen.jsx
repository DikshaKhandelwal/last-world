import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export default function HumanDecisionScreen({ pipelineOutput, onDecision }) {
  const [hovered, setHovered] = useState(null);
  const proofPanel = pipelineOutput?.proof_panel || null;
  const naiveContent = proofPanel?.naive_output ?? proofPanel?.naive_qwen;
  const systemContent = proofPanel?.system_output ?? proofPanel?.system_qwen_raw;
  const verifiedContent = proofPanel?.verified_output ?? proofPanel?.verified;

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key.toLowerCase() === 'y') onDecision(true);
      if (e.key.toLowerCase() === 'n') onDecision(false);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onDecision]);

  return (
    <div style={{
      width: '100%',
      height: '100%',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: 'rgba(8, 8, 8, 0.6)',
      backdropFilter: 'blur(8px) brightness(0.4)',
      position: 'absolute',
      top: 0,
      left: 0,
      zIndex: 100
    }}>
      <motion.div
        initial={{ opacity: 0, y: -40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.19, 1, 0.22, 1] }}
        style={{
          width: '700px',
          backgroundColor: 'var(--deep)',
          border: '1px solid var(--amber)',
          borderTop: '4px solid var(--amber)',
          boxShadow: '0 0 20px var(--amber-glow)',
          padding: '32px',
          display: 'flex',
          flexDirection: 'column',
          gap: '24px'
        }}
      >
        <div style={{
          fontFamily: 'var(--font-terminal)',
          fontSize: 'var(--text-xs)',
          letterSpacing: 'var(--tracking-widest)',
          color: 'var(--amber)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>OPERATOR JUDGMENT REQUIRED</span>
          <span style={{ animation: 'blink 1s step-end infinite' }}>[WAITING]</span>
        </div>

        {proofPanel && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'var(--text-sm)',
              color: 'var(--text-primary)',
              letterSpacing: 'var(--tracking-wider)'
            }}>
              THE GAP — WHAT QWEN 0.6B DID
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
              <PanelBlock
                title="NAIVE QWEN"
                subtitle="Direct prompt, no system"
                borderColor="var(--red)"
                background="rgba(255, 40, 40, 0.06)"
                content={naiveContent}
              />
              <PanelBlock
                title="SYSTEM QWEN"
                subtitle="Model output (unedited)"
                borderColor="var(--amber)"
                background="rgba(255, 190, 70, 0.06)"
                content={systemContent}
              />
              <PanelBlock
                title="VERIFIED OUTPUT"
                subtitle="After validation + constraints"
                borderColor="var(--green)"
                background="rgba(100, 255, 160, 0.06)"
                content={verifiedContent}
              />
            </div>

            {proofPanel.verification_line && (
              <div style={{
                fontFamily: 'var(--font-terminal)',
                fontSize: 'var(--text-xs)',
                color: 'var(--text-secondary)'
              }}>
                Verify this yourself: {proofPanel.verification_line}
              </div>
            )}
          </div>
        )}

        <div style={{
          fontFamily: 'var(--font-display)',
          fontSize: 'var(--text-xl)',
          color: 'var(--text-primary)',
          lineHeight: 1.4
        }}>
          Confirm the system output and proceed to the next crisis?
        </div>

        <div style={{
          fontFamily: 'var(--font-terminal)',
          fontSize: 'var(--text-sm)',
          color: 'var(--text-secondary)'
        }}>
          Option Y: Confirm diagnosis and apply mitigation.
          <br/>
          Option N: Reject diagnosis. Restart pipeline evaluation.
        </div>

        <div style={{ display: 'flex', gap: '16px', marginTop: '16px' }}>
          <Button 
            text="[ Y ] YES" 
            onMouseOver={() => setHovered('Y')} 
            onMouseOut={() => setHovered(null)} 
            isHovered={hovered === 'Y'} 
            onClick={() => onDecision(true)} 
          />
          <Button 
            text="[ N ] NO" 
            onMouseOver={() => setHovered('N')} 
            onMouseOut={() => setHovered(null)} 
            isHovered={hovered === 'N'} 
            onClick={() => onDecision(false)} 
          />
        </div>
      </motion.div>
    </div>
  );
}

function Button({ text, onMouseOver, onMouseOut, isHovered, onClick }) {
  return (
    <button
      onMouseOver={onMouseOver}
      onMouseOut={onMouseOut}
      onClick={onClick}
      style={{
        flex: 1,
        padding: '16px',
        backgroundColor: isHovered ? 'var(--amber)' : 'transparent',
        border: '1px solid var(--amber)',
        color: isHovered ? 'var(--black)' : 'var(--amber)',
        fontFamily: 'var(--font-terminal)',
        fontSize: 'var(--text-sm)',
        letterSpacing: 'var(--tracking-widest)',
        cursor: 'pointer',
        transition: 'all 0.15s ease'
      }}
    >
      {text}
    </button>
  );
}

function PanelBlock({ title, subtitle, borderColor, background, content }) {
  return (
    <div style={{
      border: `1px solid ${borderColor}`,
      background,
      padding: '12px',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
      minHeight: '180px'
    }}>
      <div style={{
        fontFamily: 'var(--font-terminal)',
        fontSize: 'var(--text-xs)',
        color: borderColor,
        letterSpacing: 'var(--tracking-widest)'
      }}>
        {title}
      </div>
      <div style={{
        fontFamily: 'var(--font-terminal)',
        fontSize: 'var(--text-xs)',
        color: 'var(--text-secondary)'
      }}>
        {subtitle}
      </div>
      <div className="scrollbar-hidden" style={{
        fontFamily: 'var(--font-terminal)',
        fontSize: 'var(--text-sm)',
        color: 'var(--text-primary)',
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
        overflowY: 'auto',
        maxHeight: '180px'
      }}>
        {typeof content === 'string' ? content : JSON.stringify(content, null, 2)}
      </div>
    </div>
  );
}
