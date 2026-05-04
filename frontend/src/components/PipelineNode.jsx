import React from 'react';
import { motion } from 'framer-motion';

export default function PipelineNode({ label, status, output, isLast, retries = 0 }) {
  // status: 'pending' | 'running' | 'retry' | 'success' | 'failed'
  
  const getDotStyle = () => {
    switch(status) {
      case 'running': return { backgroundColor: 'var(--amber)', size: 8, empty: false };
      case 'retry': return { backgroundColor: 'var(--red)', size: 8, empty: false };
      case 'success': return { backgroundColor: 'var(--green)', size: 8, empty: false };
      case 'failed': return { backgroundColor: 'var(--red)', size: 8, empty: false, isCross: true };
      default: return { backgroundColor: 'transparent', borderColor: 'var(--text-muted)', size: 8, empty: true };
    }
  };

  const dotSetup = getDotStyle();
  const showPulse = status === 'running' || status === 'retry';

  return (
    <motion.div 
      style={{ display: 'flex', flexDirection: 'column' }}
      animate={status === 'retry' ? { x: [0, -4, 4, -2, 2, 0] } : {}}
      transition={status === 'retry' ? { duration: 0.4 } : {}}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
        
        {/* Connection & Dot wrapper */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: '16px' }}>
          
          <div style={{ width: '16px', height: '16px', display: 'flex', justifyContent: 'center', alignItems: 'center', marginTop: '2px' }}>
            {dotSetup.isCross ? (
              <div style={{ color: 'var(--red)', fontSize: '10px', fontWeight: 'bold' }}>✕</div>
            ) : (
              <motion.div 
                style={{ 
                  width: `${dotSetup.size}px`, 
                  height: `${dotSetup.size}px`, 
                  borderRadius: '50%', 
                  backgroundColor: dotSetup.backgroundColor,
                  border: dotSetup.empty ? `1px solid ${dotSetup.borderColor}` : 'none'
                }}
                animate={showPulse ? { scale: [1, 1.3, 1] } : { scale: 1 }}
                transition={showPulse ? { repeat: Infinity, duration: status === 'retry' ? 0.4 : 1 } : {}}
              />
            )}
          </div>
          
          {!isLast && (
            <div style={{ width: '1px', backgroundColor: status === 'success' || status === 'failed' ? 'var(--green)' : 'var(--border)', minHeight: '40px', margin: '4px 0', position: 'relative' }}>
              {status === 'running' && (
                <motion.div 
                  initial={{ top: '0%', opacity: 1 }}
                  animate={{ top: '100%', opacity: 0 }}
                  transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
                  style={{ width: '3px', height: '3px', borderRadius: '50%', backgroundColor: 'var(--amber)', position: 'absolute', left: '-1px' }}
                />
              )}
            </div>
          )}
        </div>

        {/* Text Content */}
        <div style={{ display: 'flex', flexDirection: 'column', marginTop: '2px', paddingBottom: isLast ? 0 : '16px' }}>
          <div style={{ 
            fontFamily: 'var(--font-terminal)', 
            fontSize: 'var(--text-sm)', 
            color: status === 'retry' || status === 'failed' ? 'var(--red)' : 'var(--text-primary)',
            transition: 'color 0.3s'
          }}>
            {label} {retries > 0 && `[RETRY ${retries}]`}
          </div>
          
          {output && (
            <motion.div 
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              style={{
                fontFamily: 'var(--font-terminal)', 
                fontSize: 'var(--text-xs)', 
                color: 'var(--text-secondary)',
                marginTop: '4px'
              }}
            >
              {output}
            </motion.div>
          )}
        </div>

      </div>
    </motion.div>
  );
}
