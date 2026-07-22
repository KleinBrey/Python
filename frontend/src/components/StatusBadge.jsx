import React from 'react';
import { CheckCircle2, CircleDashed, XCircle } from 'lucide-react';
import { statusLabel, statusTone } from '../utils/formatters.js';

export default function StatusBadge({ status, label }) {
  const tone = statusTone(status);
  const Icon = tone === 'ok' ? CheckCircle2 : tone === 'bad' ? XCircle : CircleDashed;

  return (
    <span className={`status-badge ${tone}`}>
      <Icon size={14} />
      {label || statusLabel(status)}
    </span>
  );
}
