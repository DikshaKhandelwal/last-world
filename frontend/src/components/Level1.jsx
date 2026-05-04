import React, { useState } from 'react';
import axios from 'axios';
import Pipeline from './Pipeline';
import './Level.css';

const SAMPLE_LOGS = `[2041-05-14 03:45:22] ERROR: Service A connection timeout
[2041-05-14 03:45:23] WARN: Retry attempt 1
[2041-05-14 03:45:25] ERROR: Service A connection timeout
[2041-05-14 03:45:25] ERROR: Memory leak detected in cache layer
[2041-05-14 03:45:26] WARN: Garbage collection triggered
[2041-05-14 03:45:27] ERROR: Service B failed to initialize - dependency A missing
[2041-05-14 03:45:28] ERROR: Database connection lost
[2041-05-14 03:45:29] FATAL: Cascade failure initiated
[2041-05-14 03:45:30] WARN: 14 services degraded`;

export default function Level1({ onReturn }) {
  const [logsInput, setLogsInput] = useState(SAMPLE_LOGS);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [pipelineNodes, setPipelineNodes] = useState([]);

  const handleAnalyze = async () => {
    setLoading(true);
    setPipelineNodes([
      { name: 'DEDUP', status: 'pending' },
      { name: 'TIMESTAMP_EXTRACT', status: 'pending' },
      { name: 'ANOMALY_ISOLATION', status: 'pending' },
      { name: 'LINE_CLASSIFY', status: 'pending' },
      { name: 'CAUSE_INFERENCE', status: 'pending' },
      { name: 'BLAST_RADIUS', status: 'pending' },
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

        if (i === 4) {
          // Simulate a retry
          await new Promise(resolve => setTimeout(resolve, 400));
          setPipelineNodes(n => {
            const updated = [...n];
            updated[i].status = 'retry';
            return updated;
          });
          await new Promise(resolve => setTimeout(resolve, 400));
        }

        setPipelineNodes(n => {
          const updated = [...n];
          updated[i].status = 'success';
          return updated;
        });
      }

      const response = await axios.post('/api/level1', { logs: logsInput });
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
        <h1>Level 1: The Cascade</h1>
        <p className="subtitle">03:47 AM. Memory leak. Cascade failure. 14 services down. 11 minutes to SLA breach.</p>
      </div>

      <div className="level-content">
        <div className="input-section">
          <h2>Paste Your Server Logs</h2>
          <textarea
            value={logsInput}
            onChange={e => setLogsInput(e.target.value)}
            placeholder="Paste logs here..."
            className="log-input"
            rows="12"
          />
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="analyze-btn"
          >
            {loading ? 'Analyzing...' : 'Analyze with Qwen 0.6B'}
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
                  <h3>Cascade Origin Detected</h3>
                  <div className="metric">
                    <span className="metric-label">Service:</span>
                    <span className="metric-value">{result.analysis.origin}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Services Affected:</span>
                    <span className="metric-value">{result.analysis.servicesAffected}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Blast Radius:</span>
                    <code>{result.analysis.cascadePath.join(' → ')}</code>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Recommendation:</span>
                    <p>{result.analysis.recommendation}</p>
                  </div>
                </div>

                {result.classified && (
                  <div className="classified-panel">
                    <h3>Model Classifications</h3>
                    <div className="classification-list">
                      {result.classified.map((item, idx) => (
                        <div key={idx} className="classification-item">
                          <span className="class-badge">{item.classification}</span>
                          <span className="class-line">{item.line.substring(0, 60)}...</span>
                        </div>
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
