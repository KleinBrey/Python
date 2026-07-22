export const dashboardGroups = [
  {
    title: '看板',
    items: [
      {
        id: 'hot-rankings',
        path: '/hot-rankings',
        title: '股票热度',
        description: '雪球、东方财富、百度热搜榜单',
        status: '已接入',
      },
      {
        id: 'market-overview',
        path: '/market-overview',
        title: '市场概览',
        description: '指数、涨跌分布、成交概览',
        status: '已接入',
      },
      {
        id: 'strategy-signals',
        path: '/strategy-signals',
        title: '策略信号',
        description: '问财选股、手写策略和统一股票列表',
        status: '已接入',
      },
      {
        id: 'iwencai-selector',
        path: '/iwencai-selector',
        title: '问财选股',
        description: '自然语言条件查询与股票列表',
        status: '已接入',
      },
      {
        id: 'chart-center',
        path: '/chart-center',
        title: '图表中心',
        description: '历史行情和自定义图表',
        status: '规划中',
      },
    ],
  },
  {
    title: '数据',
    items: [
      {
        id: 'data-sources',
        path: '/data-sources',
        title: '数据源',
        description: 'AkShare、东方财富、Tushare',
        status: '查看',
      },
      {
        id: 'database',
        path: '/database',
        title: 'MongoDB',
        description: '缓存、采集结果、策略结果',
        status: '查看',
      },
    ],
  },
];

export const defaultDashboardPath = '/hot-rankings';

export function getDashboardByPath(pathname) {
  return dashboardGroups
    .flatMap((group) => group.items)
    .find((item) => item.path === pathname);
}
