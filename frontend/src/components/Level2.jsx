import React, { useState } from 'react';
import axios from 'axios';
import Pipeline from './Pipeline';
import './Level.css';

const SAMPLE_CONTRACT = `TREATY ON EMERGENCY RESOURCE SHARING - ARTICLE 91

Whereas, the undersigned parties ("the Parties") agree to establish this binding agreement on May 14, 2041;

1. DEFINITIONS
   1.1 "Critical Resources" shall mean medical supplies, fuel, water, and telecommunications infrastructure.
   1.2 "The Authority" means the Emergency Coordination Council established herein.
   1.3 "Signatory Nation" refers to any nation that has executed this Treaty.

2. RESOURCE ALLOCATION
   2.1 Each Signatory Nation shall contribute 15% of Critical Resources inventory to the shared pool.
   2.2 The Authority shall distribute resources based on demonstrated need.
   2.3 No Signatory Nation may prioritize domestic needs over Treaty obligations.

3. DISPUTE RESOLUTION
   3.1 The Authority shall resolve all conflicts between parties.
   3.2 Each party retains sovereign right to withdraw resources if domestic crisis exceeds threshold.
   3.3 In case of unresolved contradiction, this Treaty becomes void automatically.

Article I: Authority Powers
   The Authority may commandeer resources from any nation at will.
   The Authority must respect national sovereignty in all decisions.

Article II: Withdrawal Rights
   Nations may not withdraw resources once committed.
   Nations retain absolute rights to withdraw resources for domestic use.

ARTICLE 91 - CONFLICT RESOLUTION
If any two articles of this Treaty contradict, the Treaty is void within 120 minutes of discovery.
Current violations detected: 3
Time remaining: 2 hours 14 minutes`;

export default function Level2({ onReturn }) {
  const [contractInput, setContractInput] = useState(SAMPLE_CONTRACT);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [pipelineNodes, setPipelineNodes] = useState([]);

  const handleAnalyze = async () => {
    setLoading(true);
    setPipelineNodes([
      { name: 'DEFINED_TERMS', status: 'pending' },
      { name: 'CLAUSE_SEGMENT', status: 'pending' },
      { name: 'REFERENCE_GRAPH', status: 'pending' },
      { name: 'CONFLICT_DETECT', status: 'pending' },
      { name: 'AMBIGUITY_CHECK', status: 'pending' },
      { name: 'TRANSLATION', status: 'pending' },
      { name: 'OUTPUT', status: 'pending' },
    ]);

    try {
      // Simulate node execution
      for (let i = 0; i < pipelineNodes.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 600));
        setPipelineNodes(n => {
          const updated = [...n];
          updated[i].status = 'executing';
          return updated;
        });

        if (i === 3) {
          // Simulate conflict detection with retry
          await new Promise(resolve => setTimeout(resolve, 500));
          setPipelineNodes(n => {
            const updated = [...n];
            updated[i].status = 'retry';
            return updated;
          });
          await new Promise(resolve => setTimeout(resolve, 500));
        }

        setPipelineNodes(n => {
          const updated = [...n];
          updated[i].status = 'success';
          return updated;
        });
      }

      const response = await axios.post('/api/level2', { contract: contractInput });
      setResult(response.data);
    } catch (error) {
      console.error('Analysis failed:', error);
      setResult({
        error: error.response?.data?.error || error.message,
      });
      setPipelineNodes(n =>
        n.map(node => ({ ...node, status: node.status === 'executing' ? 'failed' : node.status }))
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="level">
      <div className="level-header">
        <button className="back-btn" onClick={onReturn}>← Back</button>
        <h1>Level 2: The Silent Clause</h1>
        <p className="subtitle">04:12 AM. 40-nation treaty. 31 signatures. Legal contradictions detected. 2 hours to void.</p>
      </div>

      <div className="level-content">
        <div className="input-section">
          <h2>Paste Contract or Legal Text</h2>
          <textarea
            value={contractInput}
            onChange={e => setContractInput(e.target.value)}
            placeholder="Paste contract text here..."
            className="log-input"
            rows="14"
          />
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="analyze-btn"
          >
            {loading ? 'Analyzing...' : 'Analyze Legal Text with Qwen 0.6B'}
          </button>
        </div>

        {pipelineNodes.length > 0 && (
          <Pipeline nodes={pipelineNodes} />
        )}

        {result && (
          <div className="result-section">
            {result.error ? (
              <div className="error-panel">
                <h3>❌ Analysis Failed</h3>
                <p>{result.error}</p>
              </div>
            ) : (
              <>
                <div className="analysis-panel">
                  <h3>Legal Analysis Complete</h3>
                  <div className="metric">
                    <span className="metric-label">Clauses:</span>
                    <span className="metric-value">{result.analysis.clausesReviewed}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Conflicts:</span>
                    <span className="metric-value" style={{ color: result.analysis.conflictsDetected > 0 ? 'var(--danger)' : 'var(--ok)' }}>
                      {result.analysis.conflictsDetected}
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Ambiguous Terms:</span>
                    <span className="metric-value">{result.analysis.ambiguousTerms}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Status:</span>
                    <span className="metric-value">
                      {result.analysis.requiresHumanReview ? '⚠ Requires Human Review' : '✓ Approved'}
                    </span>
                  </div>
                </div>

                {result.analysis.conflicts && result.analysis.conflicts.length > 0 && (
                  <div className="classified-panel">
                    <h3>Detected Conflicts</h3>
                    <div className="classification-list">
                      {result.analysis.conflicts.map((conflict, idx) => (
                        <div key={idx} className="classification-item">
                          <span className="class-badge" style={{ background: 'var(--danger)' }}>CONFLICT</span>
                          <span className="class-line">Article {conflict.clause1 + 1} ↔ Article {conflict.clause2 + 1}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {result.definedTerms && result.definedTerms.length > 0 && (
                  <div className="classified-panel">
                    <h3>Defined Terms Found</h3>
                    <div className="terms-list">
                      {result.definedTerms.map((term, idx) => (
                        <span key={idx} className="term-tag">{term}</span>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
