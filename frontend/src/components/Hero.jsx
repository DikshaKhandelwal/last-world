import React from 'react';
import './Hero.css';

export default function Hero({ onSelectLevel }) {
  return (
    <div className="hero">
      <nav className="nav">
        <div className="logo">GARAGE_INFERENCE × LAST_MODEL</div>
        <div className="nav-links">
          <a href="#tiers">Model Tiers</a>
          <a href="#levels">Levels</a>
          <a href="#judging">Judging</a>
        </div>
      </nav>

      <div className="hero-content">
        <p className="eyebrow">MAY 1-4, 2026 | ONLINE | LIVE</p>
        <h1>
          The smallest model that still<br />
          <span>saves the world.</span>
        </h1>
        <p className="lead">
          When the frontier systems went dark in 2041, one 0.6B parameter model remained.
          It's barely capable. The world doesn't know. You must make it work.
        </p>

        <div className="level-grid">
          <div className="level-card" onClick={() => onSelectLevel('1')}>
            <h3>Level 1: The Dead Code</h3>
            <p>Code review under fire. Find the failure condition.</p>
            <span className="cta-inline">Enter →</span>
          </div>
          <div className="level-card" onClick={() => onSelectLevel('2')}>
            <h3>Level 2: The Rigged Question</h3>
            <p>Argument analysis. Extract claims and expose the fallacy.</p>
            <span className="cta-inline">Enter →</span>
          </div>
          <div className="level-card disabled">
            <h3>Level 3: The Wrong Person</h3>
            <p>Incoming — Behavioral anomalies in response logs</p>
          </div>
          <div className="level-card disabled">
            <h3>Level 4: The Corrupted Oracle</h3>
            <p>Incoming — Forensic analysis of corrupted data</p>
          </div>
        </div>

        <div className="stats">
          <div className="stat">
            <div className="stat-value">72</div>
            <div className="stat-label">Hours to build</div>
          </div>
          <div className="stat">
            <div className="stat-value">0.6B</div>
            <div className="stat-label">Parameter model</div>
          </div>
          <div className="stat">
            <div className="stat-value">5</div>
            <div className="stat-label">Critical failures</div>
          </div>
          <div className="stat">
            <div className="stat-value">$1.7K</div>
            <div className="stat-label">Prizes</div>
          </div>
        </div>
      </div>
    </div>
  );
}
