import MarketOverviewView from '@/features/market-overview/components/MarketOverviewView.jsx';

import { useState } from 'react';
import { Calendar } from '@/shadcn/components/ui/calendar';
export default function MarketOverview() {
  return <MarketOverviewView />;
}

// export default function MyCalendar() {
//   const [date, setDate] = useState(new Date());

//   return <Calendar mode="single" selected={date} onSelect={setDate} className="rounded-md border" />;
// }
