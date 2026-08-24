import { Braces, FileSearch, Layers3 } from 'lucide-react';

import StatusBadge from '@/components/StatusBadge.jsx';
import { formatValue, shortTime } from '@/utils/formatters.js';

const sourceIcons = { iwencai: FileSearch, handwritten: Braces };

export default function SourceCard({ source }) {
  const Icon = sourceIcons[source.id] || Layers3;
  const detail = source.id === 'iwencai'
    ? source.metadata?.resultFile
    : (source.metadata?.strategies || []).map(item => item.name).join('、');

  return (
    <article className="strategy-source-card">
      <div className="strategy-source-head">
        <div className="strategy-source-title">
          <span className={`strategy-source-icon ${source.id}`}><Icon size={18} /></span>
          <div><h3>{source.name}</h3><p>{source.description}</p></div>
        </div>
        <StatusBadge status={source.status} />
      </div>
      <div className="strategy-source-meta">
        <div><span>股票数量</span><strong>{formatValue(source.stockCount)}</strong></div>
        <div><span>更新时间</span><strong>{shortTime(source.updatedAt)}</strong></div>
      </div>
      {detail ? <p className="strategy-source-detail" title={detail}>{detail}</p> : null}
      {source.error ? <div className="inline-error">{source.error}</div> : null}
    </article>
  );
}
