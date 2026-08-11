import { React, useContext } from 'react';
import {
  BarChart3,
  ChartNoAxesCombined,
  Database,
  BadgeDollarSign,
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
import style from './Layout.module.css';
import { ThemeContext } from '@/contexts';


const iconById = {
  'hot-rankings': TrendingUp,
  'market-overview': PieChart,
  'strategy-signals': ChartNoAxesCombined,
  'iwencai-selector': Search,
  'chart-center': BarChart3,
  'data-sources': LayoutDashboard,
  'database': Database,
};


export default function Layout ({ children, selectedDashboard, refreshingAll, onRefreshAll }) {

  const { theme, toggleTheme } = useContext(ThemeContext)

  console.log(theme, toggleTheme)


  return (
    <div className={style.layout}>
      <aside className={style.sidebar}>
        <div className={style.logo}>
          <div className={style.mark}>
            <BadgeDollarSign size={25} />
          </div>
          <div className={style.title}>
            <strong>Stock Core</strong>
            <span>Dashboard</span>
          </div>
        </div>

        <button onClick={toggleTheme}>
          切换主题
        </button>

        <nav className={style.sidebarNav} aria-label="股票看板导航">
          {dashboardGroups.map((group) => (
            <section key={group.title}>
              <p>{group.title}</p>
              {group.items.map((item) => {
                const Icon = iconById[item.id] || LayoutDashboard;
                return (
                  <NavLink
                    className={({ isActive }) => `${style.navItem}${isActive ? ` ${style.active}` : ''}`}
                    key={item.path}
                    title={item.description}
                    to={item.path}
                  >
                    <Icon size={16} />
                    <span>{item.title}</span>
                    <Badge className={style.navStatus} variant="secondary">{item.status}</Badge>
                  </NavLink>
                );
              })}
            </section>
          ))}
        </nav>

        <div className={style.sidebarFooter}>
          <Server size={16} />
          <span>本地数据服务<br />127.0.0.1:8001</span>
        </div>
      </aside>

      <div className={style.mainArea}>
        <header className={style.siteHeader}>
          <div className={style.headerTitle}>
            <div>
              <h1>股票看板中心</h1>
              <span>{selectedDashboard?.title || 'Dashboard'}</span>
            </div>
          </div>
        </header>
        <main className={style.stockContent}>{children}</main>
      </div>
    </div>
  );
}
