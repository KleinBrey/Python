import StrategySignalsView from '@/features/strategy-signals/components/StrategySignalsView.jsx';
import { useStrategySignals } from '@/features/strategy-signals/hooks/useStrategySignals.js';

export default function StrategySignalsDashboard() {
  return <StrategySignalsView state={useStrategySignals()} />;
}
