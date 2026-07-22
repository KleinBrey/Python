import React from 'react';
import { formatValue } from '../utils/formatters.js';

export default function MetricCard({ label, value, note, icon: Icon, tone = 'neutral' }) {
  return (
    <article className="metric-card">
      <div className="metric-head">
        <span>{label}</span>
        <div className={`metric-icon ${tone}`}>
          <Icon size={17} />
        </div>
      </div>
      <strong>{formatValue(value)}</strong>
      <p>{note}</p>
    </article>
  );
}
