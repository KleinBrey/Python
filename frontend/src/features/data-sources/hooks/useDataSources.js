import { useCallback, useRef, useState } from 'react';

import { syncDailyK, syncHotStock, syncStockList } from '../api/dataSourcesApi.js';

const SYNC_TASKS = [
  {
    id: 'hot-stock',
    name: '股票热度',
    description: '获取当天 A 股热度榜，并更新股票热度数据表。',
    run: syncHotStock
  },
  {
    id: 'daily-k',
    name: '日 K 线数据',
    description: '同步最近 3 个自然日的行情，每批处理 100 只股票。',
    run: syncDailyK
  },
  {
    id: 'stock-list',
    name: 'A 股股票列表',
    description: '拉取并写入最新 A 股基础信息，建议先执行这个任务。',
    run: syncStockList
  }
];

const INITIAL_RESULTS = Object.fromEntries(
  SYNC_TASKS.map(task => [task.id, { status: 'idle', message: '', finishedAt: '', duration: null }])
);

export function useDataSources() {
  const [results, setResults] = useState(INITIAL_RESULTS);
  const [error, setError] = useState('');
  const activeTask = useRef(null);

  const runSync = useCallback(async taskId => {
    if (activeTask.current) return;

    const task = SYNC_TASKS.find(item => item.id === taskId);
    if (!task) return;

    activeTask.current = taskId;
    setError('');
    setResults(current => ({
      ...current,
      [taskId]: { status: 'running', message: '正在执行同步脚本…', finishedAt: '', duration: null }
    }));

    try {
      const { data } = await task.run();
      setResults(current => ({
        ...current,
        [taskId]: {
          status: 'success',
          message: data.message,
          finishedAt: data.finished_at,
          duration: data.duration_seconds
        }
      }));
    } catch (requestError) {
      const message = requestError.response?.data?.detail || requestError.message || '同步脚本执行失败';
      setError(`${task.name}：${message}`);
      setResults(current => ({
        ...current,
        [taskId]: { status: 'failed', message: '同步脚本执行失败', finishedAt: '', duration: null }
      }));
    } finally {
      activeTask.current = null;
    }
  }, []);

  const runningTaskId = Object.keys(results).find(taskId => results[taskId].status === 'running') || null;

  return {
    tasks: SYNC_TASKS,
    results,
    runningTaskId,
    error,
    runSync
  };
}
