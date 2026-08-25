import { Braces, FileSearch, Layers3 } from 'lucide-react';

import StatusBadge from '@/components/StatusBadge.jsx';
import { cn } from '@/shadcn/lib/utils.js';
import { formatValue, shortTime } from '@/utils/formatters.js';
import styles from './StrategySignals.module.css';

const sourceIcons = { iwencai: FileSearch, handwritten: Braces };

export default function SourceCard({ source }) {
  const Icon = sourceIcons[source.id] || Layers3;
  const detail = source.id === 'iwencai'
    ? source.metadata?.resultFile
    : (source.metadata?.strategies || []).map(item => item.name).join('、');

  return (
    <article className={styles.sourceCard}>
      <div className={styles.sourceHead}>
        <div className={styles.sourceTitle}>
          <span className={cn(styles.sourceIcon, styles[source.id])}><Icon size={18} /></span>
          <div><h3>{source.name}</h3><p>{source.description}</p></div>
        </div>
        <StatusBadge status={source.status} />
      </div>
      <div className={styles.sourceMeta}>
        <div><span>股票数量</span><strong>{formatValue(source.stockCount)}</strong></div>
        <div><span>更新时间</span><strong>{shortTime(source.updatedAt)}</strong></div>
      </div>
      {detail ? <p className={styles.sourceDetail} title={detail}>{detail}</p> : null}
      {source.error ? <div className={styles.inlineError}>{source.error}</div> : null}
    </article>
  );
}
