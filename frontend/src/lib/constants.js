export const LEVELS = [
  {
    id: 1,
    name: 'DEAD CODE',
    location: { lat: 37.7, lon: -122.4, name: 'San Francisco' },
    domain: 'Code Review / Reliability',
    system: 'Payment Authorization Core',
    priority: 'OMEGA / FINANCIAL',
    impact: 'Revenue Freefall',
    narrative: [
      "03:47 AM. Fraud alarms are firing.",
      "The payment processor is losing $4,000 per minute.",
      "Engineers say the bug is in the auth flow. No one can find it.",
      "You have the code. You have a 0.6B model.",
      "Find the failure condition before the rollback window closes."
    ]
  },
  {
    id: 2,
    name: 'RIGGED QUESTION',
    location: { lat: 46.2, lon: 6.1, name: 'Geneva' },
    domain: 'Argument Analysis',
    system: 'Broadcast Intelligence Desk',
    priority: 'ALPHA / SEVERE',
    impact: 'Policy Misfire',
    narrative: [
      "04:12 AM. A political statement just went viral.",
      "Three governments are about to act on it.",
      "The argument sounds convincing but is structurally flawed.",
      "You have the text. Find the fallacy before the response is locked in."
    ]
  },
  {
    id: 3,
    name: 'WRONG PERSON',
    location: { lat: 55.7, lon: 37.6, name: 'Moscow' },
    domain: 'Behavioral Anomaly Detection',
    system: 'Incident Response Comms',
    priority: 'BETA / HIGH',
    impact: 'Insider Compromise',
    narrative: [
      "05:03 AM. Six engineers had access to the compromised server.",
      "One of them is not who they claim to be.",
      "You have their incident messages.",
      "Find the outlier by how they write, not what they claim."
    ]
  },
  {
    id: 4,
    name: 'CORRUPTED ORACLE',
    location: { lat: -1.3, lon: 36.8, name: 'Nairobi' },
    domain: 'Data Forensics',
    system: 'Humanitarian Allocation Model',
    priority: 'DELTA / CRITICAL',
    impact: 'Aid Misallocation',
    narrative: [
      "06:30 AM. The dataset feeding the aid model is corrupted.",
      "Every minute of delay costs real allocation accuracy.",
      "You have the raw table. Find the impossible values.",
      "Prove each finding with a row and column."
    ]
  },
  {
    id: 5,
    name: 'LAST TRANSLATION',
    location: { lat: 40.7, lon: -74.0, name: 'New York' },
    domain: 'Crisis Communication',
    system: 'Public Broadcast Relay',
    priority: 'OMEGA / FINAL',
    impact: 'Mass Panic / Collapse',
    narrative: [
      "10:00 AM. The technical report is unreadable to the public.",
      "You have one final broadcast window.",
      "Translate the facts to Grade 6, under 100 words.",
      "No technical terms. No hallucinations."
    ]
  }
];