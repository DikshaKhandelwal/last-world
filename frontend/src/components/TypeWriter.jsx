import React, { useState, useEffect } from 'react';

export default function TypeWriter({ text, speed = 30, onComplete, className, style }) {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    let index = 0;
    
    // Reset state when text changes
    setDisplayedText('');
    setIsComplete(false);

    if (!text) {
      if (onComplete) onComplete();
      return;
    }

    const timer = setInterval(() => {
      setDisplayedText((prev) => {
        const next = text.slice(0, index + 1);
        index++;
        if (index === text.length) {
          clearInterval(timer);
          setIsComplete(true);
          if (onComplete) onComplete();
        }
        return next;
      });
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed, onComplete]);

  return (
    <div className={className} style={{ position: 'relative', display: 'inline-block', ...style }}>
      {displayedText}
      {!isComplete && (
        <span
          style={{
            display: 'inline-block',
            width: '8px',
            height: '1em',
            backgroundColor: 'var(--amber)',
            animation: 'blink 1s step-end infinite',
            verticalAlign: 'bottom',
            marginLeft: '4px'
          }}
        />
      )}
    </div>
  );
}
