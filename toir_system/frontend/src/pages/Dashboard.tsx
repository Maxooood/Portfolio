import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend,
} from 'recharts';
import { analyticsApi } from '../api/analytics';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';
import type { DashboardStats } from '../types';

const STATUS_COLORS: Record<string, string> = {
  new: '#3b82f6',
  assigned: '#f59e0b',
  in_progress: '#8b5cf6',
  waiting_parts: '#f97316',
  completed: '#10b981',
  closed: '#6b7280',
  cancelled: '#ef4444',
};

const PRIORITY_COLORS: Record<string, string> = {
  low: '#9ca3af',
  medium: '#3b82f6',
  high: '#f97316',
  critical: '#ef4444',
};

interface KpiCardProps {
  label: string;
  value: number;
  color: string;
  icon: string;
}

const KpiCard: React.FC<KpiCardProps> = ({ label, value, color, icon }) => (
  <div className={`bg-white rounded-xl shadow p-5 border-l-4 ${color}`}>
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
      </div>
      <span className="text-4xl">{icon}</span>
    </div>
  </div>
);

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    analyticsApi.getDashboard().then(setStats).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (!stats) return null;

  const statusData = stats.requests_by_status.map((s) => ({
    name: s.status,
    value: s.count,
    fill: STATUS_COLORS[s.status] ?? '#9ca3af',
  }));

  const priorityData = stats.requests_by_priority.map((p) => ({
    name: p.priority,
    value: p.count,
    fill: PRIORITY_COLORS[p.priority] ?? '#9ca3af',
  }));

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          label="Открытых заявок"
          value={stats.total_open_requests}
          color="border-blue-500"
          icon="📋"
        />
        <KpiCard
          label="Критических заявок"
          value={stats.critical_requests}
          color="border-red-500"
          icon="🚨"
        />
        <KpiCard
          label="Просрочено ППР"
          value={stats.overdue_ppr_tasks}
          color="border-orange-500"
          icon="⏰"
        />
        <KpiCard
          label="Неисправного оборудования"
          value={stats.equipment_broken}
          color="border-yellow-500"
          icon="🔩"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow p-5">
          <h2 className="text-base font-semibold text-gray-700 mb-4">Заявки по статусам</h2>
          {statusData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={statusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                  {statusData.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-sm text-center py-10">Нет данных</p>
          )}
        </div>

        <div className="bg-white rounded-xl shadow p-5">
          <h2 className="text-base font-semibold text-gray-700 mb-4">Заявки по приоритетам</h2>
          {priorityData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={priorityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" name="Заявки">
                  {priorityData.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-sm text-center py-10">Нет данных</p>
          )}
        </div>
      </div>

      {/* Recent activity */}
      <div className="bg-white rounded-xl shadow p-5">
        <h2 className="text-base font-semibold text-gray-700 mb-4">Последние заявки</h2>
        {stats.recent_activity.length === 0 ? (
          <p className="text-gray-400 text-sm">Нет активности</p>
        ) : (
          <div className="space-y-2">
            {stats.recent_activity.map((item: any) => (
              <div
                key={item.id}
                onClick={() => navigate(`/requests/${item.id}`)}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors border border-gray-100"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono text-gray-500">{item.request_number}</span>
                  <span className="text-sm text-gray-800">{item.title}</span>
                </div>
                <div className="flex items-center gap-2">
                  <PriorityBadge priority={item.priority} />
                  <StatusBadge status={item.status} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
