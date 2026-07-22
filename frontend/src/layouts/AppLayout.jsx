import React from 'react';
import {
  BarChart3,
  ChartNoAxesCombined,
  Database,
  Gauge,
  LayoutDashboard,
  PieChart,
  RefreshCw,
  Search,
  Server,
  TrendingUp,
} from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { Badge } from '@/components/ui/badge.jsx';
import { Button } from '@/components/ui/button.jsx';
import { dashboardGroups } from '../config/dashboardRegistry.js';

const iconById = {
  'hot-rankings': TrendingUp,
  'market-overview': PieChart,
  'strategy-signals': ChartNoAxesCombined,
  'iwencai-selector': Search,
  'chart-center': BarChart3,
  'data-sources': LayoutDashboard,
  database: Database,
};

export default function AppLayout({ children, selectedDashboard, refreshingAll, onRefreshAll }) {
  return (
    <div className="app-frame">
      <aside className="app-sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Gauge size={18} />
          </div>
          <div>
            <strong>Stock Core</strong>
            <span>Dashboard</span>
          </div>
        </div>

        <Button
          className="quick-action"
          disabled={refreshingAll}
          onClick={onRefreshAll}
          size="lg"
        >
          <RefreshCw className={refreshingAll ? 'spin' : ''} size={16} />
          {refreshingAll ? '正在刷新' : '刷新全部'}
        </Button>

        <nav className="sidebar-nav" aria-label="股票看板导航">
          {dashboardGroups.map((group) => (
            <section key={group.title}>
              <p>{group.title}</p>
              {group.items.map((item) => {
                const Icon = iconById[item.id] || LayoutDashboard;
                return (
                  <NavLink
                    className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
                    key={item.path}
                    title={item.description}
                    to={item.path}
                  >
                    <Icon size={16} />
                    <span>{item.title}</span>
                    <Badge className="nav-status" variant="secondary">{item.status}</Badge>
                  </NavLink>
                );
              })}
            </section>
          ))}
        </nav>

        <div className="sidebar-footer">
          <Server size={16} />
          <span>本地数据服务<br />127.0.0.1:8001</span>
        </div>
      </aside>

      <div className="main-area">
        <header className="site-header">
          <div className="header-title">
            <div>
              <h1>股票看板中心</h1>
              <span>{selectedDashboard?.title || 'Dashboard'}</span>
            </div>
          </div>
        </header>
        <main className="stock-content">{children}</main>
      </div>
    </div>
  );
}
