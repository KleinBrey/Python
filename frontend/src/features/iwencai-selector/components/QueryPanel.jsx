import { Loader2, Play } from 'lucide-react';

import { Badge } from '@/shadcn/components/ui/badge.jsx';
import { Button } from '@/shadcn/components/ui/button.jsx';
import { Textarea } from '@/shadcn/components/ui/textarea.jsx';
import { exampleQueries } from '../constants.js';
import styles from './IwencaiSelector.module.css';

export default function QueryPanel({ query, onQueryChange, status, apiKeyBadge, loading, onSubmit }) {
  return (
    <section className="dashboard-panel">
      <div className="dashboard-panel-header">
        <div><h2>自然语言问财选股</h2><span>写下行情、技术、财务或行业条件，系统会自动获取全部分页</span></div>
        <Badge variant={status?.configured ? 'success' : status ? 'warning' : 'secondary'}>{apiKeyBadge}</Badge>
      </div>
      <div className={styles.queryBody}>
        <div className={styles.textareaField}>
          <Textarea aria-label="问财查询条件" maxLength={2000} onChange={event => onQueryChange(event.target.value)} placeholder="例如：总市值大于100亿，非ST，最近5日涨幅大于5%，按个股热度排序" rows={5} value={query} />
          <span>{query.length} / 2000</span>
        </div>
        <div className={styles.examples}>
          <span>示例条件</span>
          {exampleQueries.map((example, index) => <Button key={example} type="button" onClick={() => onQueryChange(example)} size="sm" variant="outline">示例 {index + 1}</Button>)}
        </div>
        <div className={styles.queryActions}>
          <p>数据来源：同花顺问财。查询结果是研究候选集合，不构成投资建议。</p>
          <Button onClick={onSubmit} size="lg" type="button" disabled={!query.trim() || loading || !status?.configured}>
            {loading ? <Loader2 className="dashboard-spin" size={16} /> : <Play size={16} />}
            {loading ? '正在查询并获取全部分页' : '开始选股'}
          </Button>
        </div>
      </div>
    </section>
  );
}
