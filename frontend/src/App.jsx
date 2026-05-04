import React, { useState, useEffect } from 'react';
import './styles/global.css';
import BootScreen from './screens/BootScreen';
import IntroScreen from './screens/IntroScreen';
import GlobeScreen from './screens/GlobeScreen';
import LevelBriefing from './screens/LevelBriefing';
import InputScreen from './screens/InputScreen';
import PipelineScreen from './screens/PipelineScreen';
import HumanDecisionScreen from './screens/HumanDecisionScreen';
import OutcomeScreen from './screens/OutcomeScreen';
import FinaleScreen from './screens/FinaleScreen';

const SCREENS = {
  BOOT: 'BOOT',
  INTRO: 'INTRO',
  GLOBE: 'GLOBE',
  BRIEFING: 'BRIEFING',
  INPUT: 'INPUT',
  PIPELINE: 'PIPELINE',
  DECISION: 'DECISION',
  OUTCOME: 'OUTCOME',
  ENDING: 'ENDING'
};

export default function App() {
  const [screen, setScreen] = useState(SCREENS.BOOT);
  const [level, setLevel] = useState(1);
  const [isSuccess, setIsSuccess] = useState(true);
  const [sessionId, setSessionId] = useState(null);
  const [pipelineOutput, setPipelineOutput] = useState(null);
  const [inputData, setInputData] = useState('');

  useEffect(() => {
    // Start backend session silently on mount
    fetch('http://localhost:8000/api/game/start', { method: 'POST' })
      .then(res => res.json())
      .then(data => setSessionId(data.session_id))
      .catch(err => console.error("Could not start session:", err));
  }, []);

  // Hidden debug/demo shortcut handler
  useEffect(() => {
    const handleKeyPress = (e) => {
      // Press Ctrl+Shift+Number (1-5) to skip to that level's briefing
      if (e.ctrlKey && e.shiftKey && e.key >= '1' && e.key <= '5') {
        setLevel(parseInt(e.key));
        setScreen(SCREENS.BRIEFING);
      }
    };
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      {/* Dev helper overlay */}
      <div style={{ 
        position: 'absolute', top: '10px', right: '10px', 
        fontSize: '10px', color: 'var(--text-dim)', 
        zIndex: 9999, pointerEvents: 'none' 
      }}>
        [DEMO: CTRL+SHIFT+1/2/3/4/5]
      </div>
      {screen === SCREENS.BOOT && (
        <BootScreen onComplete={() => setScreen(SCREENS.INTRO)} />
      )}
      {screen === SCREENS.INTRO && (
        <IntroScreen onComplete={() => setScreen(SCREENS.GLOBE)} />
      )}
      {screen === SCREENS.GLOBE && (
        <GlobeScreen 
          level={level} 
          onComplete={() => setScreen(SCREENS.BRIEFING)} 
        />
      )}
      {screen === SCREENS.BRIEFING && (
        <LevelBriefing 
          level={level} 
          onEnterMission={() => setScreen(SCREENS.INPUT)} 
        />
      )}
      {screen === SCREENS.INPUT && (
        <InputScreen 
          level={level} 
          sessionId={sessionId}
          onComplete={(inputData) => {
            setInputData(inputData);
            setScreen(SCREENS.PIPELINE);
          }}
        />
      )}
      {screen === SCREENS.PIPELINE && (
        <PipelineScreen 
          level={level}
          inputData={inputData}
          sessionId={sessionId}
          onComplete={(finalOutput) => {
            setPipelineOutput(finalOutput);
            setScreen(SCREENS.DECISION);
          }}
        />
      )}
      {screen === SCREENS.DECISION && (
        <HumanDecisionScreen 
          pipelineOutput={pipelineOutput}
          onDecision={(decision) => {
            setIsSuccess(decision);
            setScreen(SCREENS.OUTCOME);
          }}
        />
      )}
      {screen === SCREENS.OUTCOME && (
        <OutcomeScreen 
          success={isSuccess}
          isFinalCrisis={level >= 5}
          onContinue={() => {
            if (level < 5) {
              setLevel(prev => prev + 1);
              setScreen(SCREENS.GLOBE);
            } else {
              setScreen(SCREENS.ENDING);
            }
          }}
        />
      )}
      {screen === SCREENS.ENDING && (
        <FinaleScreen
          onReturnToStandby={() => {
            setLevel(1);
            setPipelineOutput(null);
            setInputData('');
            setScreen(SCREENS.BOOT);
          }}
        />
      )}
    </div>
  );
}
