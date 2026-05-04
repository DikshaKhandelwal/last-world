import React from 'react';
import './PipelineViz.css';

const legendItems = [
  {
    key: 'naive',
    title: 'Naive Qwen',
    color: 'var(--red)',
    glow: 'var(--red-glow)',
    body:
      'Same model, one broad prompt on your input — no pipeline, no validation. This is the baseline: often generic or wrong.',
  },
  {
    key: 'system',
    title: 'System Qwen',
    color: 'var(--amber)',
    glow: 'var(--amber-glow)',
    body:
      'Same model on a narrow, structured task only (e.g. one sentence, one list). Shown verbatim — what the model actually returned for that step.',
  },
  {
    key: 'verified',
    title: 'Post-processed (verified)',
    color: 'var(--green)',
    glow: 'var(--green-glow)',
    body:
      'After rules, checks, and assembly: the structured result you can audit against your source (line numbers, flags, tables, etc.).',
  },
];

export default function ProofPanel({ proof }) {
  if (!proof) return null;

  const naive = proof.naive_output || proof.naive_qwen || '';
  const systemRaw = proof.system_output || proof.system_qwen_raw || '';
  const verified = proof.verified_output || proof.verified || '';
  const verificationLine =
    proof.verification_line || 'Verify this yourself using the source input and highlighted evidence.';

  return (
    <div style={{ border: '1px solid var(--border)', padding: '16px', background: 'var(--deep)' }}>
      <div
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: 'var(--text-sm)',
          color: 'var(--text-primary)',
          letterSpacing: 'var(--tracking-wide)',
          marginBottom: '12px',
        }}
      >
        The gap — what Qwen 0.6B did
      </div>

      <div
        style={{
          border: '1px solid var(--border-lit)',
          background: 'rgba(0,0,0,0.35)',
          padding: '14px 16px',
          marginBottom: '16px',
          borderRadius: '2px',
        }}
      >
        <div
          style={{
            fontFamily: 'var(--font-terminal)',
            fontSize: 'var(--text-xs)',
            letterSpacing: 'var(--tracking-widest)',
            color: 'var(--amber)',
            marginBottom: '12px',
          }}
        >
          WHAT EACH COLUMN MEANS
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {legendItems.map((item) => (
            <div key={item.key} style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
              <div
                aria-hidden
                style={{
                  width: '4px',
                  minHeight: '40px',
                  background: item.color,
                  boxShadow: `0 0 12px ${item.glow}`,
                  flexShrink: 0,
                  marginTop: '4px',
                }}
              />
              <div>
                <div
                  style={{
                    fontFamily: 'var(--font-terminal)',
                    fontSize: 'var(--text-sm)',
                    color: item.color,
                    marginBottom: '4px',
                  }}
                >
                  {item.title}
                </div>
                <div
                  style={{
                    fontFamily: 'var(--font-narrative)',
                    fontSize: 'var(--text-sm)',
                    color: 'var(--text-primary)',
                    lineHeight: 1.55,
                  }}
                >
                  {item.body}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px' }}>
        <div style={{ border: '1px solid var(--red)', background: 'var(--red-glow)', padding: '12px' }}>
          <div style={{ color: 'var(--red)', fontFamily: 'var(--font-terminal)', fontSize: 'var(--text-sm)', marginBottom: '6px' }}>
            NAIVE QWEN
          </div>
          <div style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)', marginBottom: '10px', lineHeight: 1.45 }}>
            Direct prompt on your full input — no system pipeline.
          </div>
          <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontSize: 'var(--text-sm)' }}>{naive}</pre>
        </div>
        <div style={{ border: '1px solid var(--amber)', background: 'var(--amber-glow)', padding: '12px' }}>
          <div style={{ color: 'var(--amber)', fontFamily: 'var(--font-terminal)', fontSize: 'var(--text-sm)', marginBottom: '6px' }}>
            SYSTEM QWEN
          </div>
          <div style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)', marginBottom: '10px', lineHeight: 1.45 }}>
            Raw model text from the narrow step only (unedited).
          </div>
          <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontSize: 'var(--text-sm)' }}>
            {typeof systemRaw === 'string' ? systemRaw : JSON.stringify(systemRaw, null, 2)}
          </pre>
        </div>
        <div style={{ border: '1px solid var(--green)', background: 'var(--green-glow)', padding: '12px' }}>
          <div style={{ color: 'var(--green)', fontFamily: 'var(--font-terminal)', fontSize: 'var(--text-sm)', marginBottom: '6px' }}>
            VERIFIED OUTPUT
          </div>
          <div style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)', marginBottom: '10px', lineHeight: 1.45 }}>
            Post-processed: validated, structured result after rules and checks.
          </div>
          <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontSize: 'var(--text-sm)' }}>
            {typeof verified === 'string' ? verified : JSON.stringify(verified, null, 2)}
          </pre>
        </div>
      </div>
      <div
        style={{
          marginTop: '14px',
          paddingTop: '12px',
          borderTop: '1px solid var(--border)',
          color: 'var(--text-secondary)',
          fontSize: 'var(--text-sm)',
          fontFamily: 'var(--font-terminal)',
          lineHeight: 1.5,
        }}
      >
        Verify this yourself: {verificationLine}
      </div>
    </div>
  );
}
