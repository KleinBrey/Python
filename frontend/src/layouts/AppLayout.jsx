import React from 'react';
import {
  AppstoreOutlined,
  BarChartOutlined,
  DatabaseOutlined,
  FundProjectionScreenOutlined,
  LineChartOutlined,
  PieChartOutlined,
  ReloadOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { Button, Layout, Menu, Space, Tag, Typography } from 'antd';
import { useLocation, useNavigate } from 'react-router-dom';
import { dashboardGroups } from '../config/dashboardRegistry.js';

const { Header, Sider, Content } = Layout;
const { Text, Title } = Typography;

const iconById = {
  'hot-rankings': <ThunderboltOutlined />,
  'market-overview': <PieChartOutlined />,
  'strategy-signals': <LineChartOutlined />,
  'chart-center': <BarChartOutlined />,
  'data-sources': <AppstoreOutlined />,
  database: <DatabaseOutlined />,
};

function buildMenuItems() {
  return dashboardGroups.map((group) => ({
    key: group.title,
    label: group.title,
    type: 'group',
    children: group.items.map((item) => ({
      key: item.path,
      icon: iconById[item.id] || <FundProjectionScreenOutlined />,
      label: (
        <span className="ant-menu-row">
          <span>{item.title}</span>
          <Tag bordered={false}>{item.status}</Tag>
        </span>
      ),
      title: item.description,
    })),
  }));
}

export default function AppLayout({ children, selectedDashboard, refreshingAll, onRefreshAll }) {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <Layout className="stock-app-layout">
      <Sider className="stock-sider" width={280} breakpoint="lg" collapsedWidth="0">
        <div className="stock-brand">
          <div className="stock-brand-mark">
            <FundProjectionScreenOutlined />
          </div>
          <div>
            <Title level={4}>Stock Core</Title>
            <Text>Dashboard</Text>
          </div>
        </div>

        <div className="stock-sider-action">
          <Button
            block
            icon={<ReloadOutlined spin={refreshingAll} />}
            loading={refreshingAll}
            onClick={onRefreshAll}
            size="large"
            type="primary"
          >
            刷新全部
          </Button>
        </div>

        <Menu
          className="stock-menu"
          items={buildMenuItems()}
          mode="inline"
          onClick={({ key }) => navigate(key)}
          selectedKeys={[location.pathname]}
          theme="dark"
        />
      </Sider>

      <Layout>
        <Header className="stock-header">
          <Space direction="vertical" size={0}>
            <Title level={2}>股票看板中心</Title>
            <Text>{selectedDashboard?.title || 'Dashboard'}</Text>
          </Space>
        </Header>

        <Content className="stock-content">
          {children}
        </Content>
      </Layout>
    </Layout>
  );
}
