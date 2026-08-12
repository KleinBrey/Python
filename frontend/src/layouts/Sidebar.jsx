import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarHeader,
} from '@/components/ui/sidebar'

import { React, useContext } from 'react'
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
} from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { Badge } from '@/components/ui/badge.jsx'
import { Button } from '@/components/ui/button.jsx'
import { dashboardGroups } from '../config/dashboardRegistry.js'
import style from './Sidebar.module.css'
import { ThemeContext } from '@/contexts'

const iconById = {
  'hot-rankings': TrendingUp,
  'market-overview': PieChart,
  'strategy-signals': ChartNoAxesCombined,
  'iwencai-selector': Search,
  'chart-center': BarChart3,
  'data-sources': LayoutDashboard,
  database: Database,
}

export function AppSidebar({ selectedDashboard }) {
  const { theme, toggleTheme } = useContext(ThemeContext)

  console.log(theme, toggleTheme)

  return (
    <Sidebar className="dark">
      <SidebarHeader>
        <div className={style.logo}>
          <div className={style.mark}>
            <img src="../../public/static/logo.png" alt="Stock Flow Logo" />
          </div>
          <div className={style.title}>
            <span>Stock Flow</span>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <aside className={style.sidebar}>
          <nav className={style.sidebarNav} aria-label="股票看板导航">
            {dashboardGroups.map((group) => (
              <section key={group.title}>
                <p>{group.title}</p>
                {group.items.map((item) => {
                  const Icon = iconById[item.id] || LayoutDashboard
                  return (
                    <NavLink
                      className={({ isActive }) =>
                        `${style.navItem}${isActive ? ` ${style.active}` : ''}`
                      }
                      key={item.path}
                      title={item.description}
                      to={item.path}
                    >
                      <Icon size={16} />
                      <span>{item.title}</span>
                    </NavLink>
                  )
                })}
              </section>
            ))}
          </nav>
        </aside>
      </SidebarContent>
      <SidebarFooter>
        <div className={style.sidebarFooter}>
          <Server size={16} />
          <span>
            本地数据服务
            <br />
            127.0.0.1:8001
          </span>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
