import React from 'react';
import { Blocks } from 'lucide-react';
import { dashboardGroups } from '../config/dashboardRegistry.js';

export default function PlaceholderDashboard({ dashboardId }) {
  const current = dashboardGroups.flatMap((group) => group.items).find((item) => item.id === dashboardId);

  return (
    <section className="placeholder">
      <Blocks size={34} />
      <h2>{current?.title || '看板'}</h2>
      <p>{current?.description || '这个看板还没有接入数据。'}</p>
    </section>
  );
}
