import React, { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, LineChart, Line,
} from 'recharts';
import { analyticsApi } from '../api/analytics';
import type { AnalyticsReport } from '../types';

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

export const Analytics: React.FC = () => {
  const [report, setReport] = useState<AnalyticsReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsApi.getReport().then(setReport).finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
    </div>
  );

  if (!report) return null;

  const statusData = report.requests_by_status.map((s) => ({
    name: s.status,
    value: s.count,
    fill: STATUS_COLORS[s.status] ?? '#9ca3af',
  }));

  const priorityData = report.requests_by_priority.map((p) => ({
    name: p.priority,
    value: p.count,
    fill: PRIORITY_COLORS[p.priority] ?? '#9ca3af',
  }));

  return (
    <div className="space-y-6">
      {/* PPR rate */}
      <div className="bg-white rounded-xl shadow p-5 flex items-center gap-6">
        <div className="text-center">
          <p className="text-sm text-gray-500">Выполнение ППР</p>
          <p className="text-4xl font-bold text-green-600">{report.ppr_completion_rate}%</p>
        </div>
        <div className="flex-1 bg-gray-200 rounded-full h-4">
          <div
            className="bg-green-500 h-4 rounded-full transition-all"
            style={{ width: `${Math.min(report.ppr_completion_rate, 100)}%` }}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status pie */}
        <div className="bg-white rounded-xl shadow p-5">
          <h2 className="text-base font-semibold text-gray-700 mb-4">Заявки по статусам</h2>
          {statusData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={statusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label={({ name, value }) => `${name}: ${value}`}>
                  {statusData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : <p className="text-gray-400 text-sm text-center py-10">Нет данных</p>}
        </div>

        {/* Priority bar */}
        <div className="bg-white rounded-xl shadow p-5">
          <h2 className="text-base font-semibold text-gray-700 mb-4">Заявки по приоритетам</h2>
          {priorityData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={priorityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" name="Заявок">
                  {priorityData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : <p className="text-gray-400 text-sm text-center py-10">Нет данных</p>}
        </div>

        {/* Equipment faults */}
        <div className="bg-white rounded-xl shadow p-5">
          <h2 className="text-base font-semibold text-gray-700 mb-4">Неисправности по оборудованию</h2>
          {report.equipment_faults.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={report.equipment_faults} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="equipment_name" type="category" width={140} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="fault_count" name="Заявок" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          ) : <p className="text-gray-400 text-sm text-center py-10">Нет данных</p>}
        </div>

        {/* Monthly requests */}
        <div className="bg-white rounded-xl shadow p-5">
          <h2 className="text-base font-semibold text-gray-700 mb-4">Заявки по месяцам</h2>
          {report.monthly_requests.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={report.monthly_requests}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="count" name="Заявок" stroke="#3b82f6" strokeWidth={2} dot />
              </LineChart>
            </ResponsiveContainer>
          ) : <p className="text-gray-400 text-sm text-center py-10">Нет данных</p>}
        </div>
      </div>

      {/* Service performance table */}
      {report.service_performance.length > 0 && (
        <div className="bg-white rounded-xl shadow p-5">
          <h2 className="text-base font-semibold text-gray-700 mb-4">Производительность служб</h2>
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left text-xs font-medium text-gray-500 uppercase">
                <th className="pb-2">Служба</th>
                <th className="pb-2">Всего заявок</th>
                <th className="pb-2">Выполнено</th>
                <th className="pb-2">% выполнения</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {report.service_performance.map((s) => (
                <tr key={s.service_id}>
                  <td className="py-2">{s.service_name}</td>
                  <td className="py-2">{s.total_requests}</td>
                  <td className="py-2">{s.completed_requests}</td>
                  <td className="py-2">
                    {s.total_requests > 0
                      ? `${Math.round((s.completed_requests / s.total_requests) * 100)}%`
                      : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
