import IwencaiSelectorView from '@/features/iwencai-selector/components/IwencaiSelectorView.jsx';
import { useIwencaiMarketData } from '@/features/iwencai-selector/hooks/useIwencaiMarketData.js';
import { useIwencaiQuery } from '@/features/iwencai-selector/hooks/useIwencaiQuery.js';

export default function IwencaiSelectorDashboard() {
  const queryState = useIwencaiQuery();
  const marketData = useIwencaiMarketData(queryState.rows, queryState.status);
  return <IwencaiSelectorView queryState={queryState} marketData={marketData} />;
}
