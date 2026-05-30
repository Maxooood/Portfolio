import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import { requestsApi } from '../api/requests';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';
import { useAuthStore } from '../store/auth';
import type { RequestDetail as TRequestDetail, Diagnostic, Repair, Report } from '../types';

export const RequestDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user, hasRole } = useAuthStore();

  const [request, setRequest] = useState<TRequestDetail | null>(null);
  const [diagnostics, setDiagnostics] = useState<Diagnostic[]>([]);
  const [repairs, setRepairs] = useState<Repair[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'info' | 'diagnostic' | 'repair' | 'report'>('info');

  // Forms
  const [diagForm, setDiagForm] = useState({ findings: '', recommended_action: '', estimated_repair_hours: '' });
  const [repairForm, setRepairForm] = useState({ work_description: '', labor_hours: '', result: '' });
  const [reportForm, setReportForm] = useState({ summary: '', recommendations: '' });

  const reqId = Number(id);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [req, diag, rep, reps] = await Promise.all([
        requestsApi.get(reqId),
        requestsApi.listDiagnostics(reqId),
        requestsApi.listRepairs(reqId),
        requestsApi.listReports(reqId),
      ]);
      setRequest(req);
      setDiagnostics(diag);
      setRepairs(rep);
      setReports(reps);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadAll(); }, [reqId]);

  const updateStatus = async (newStatus: string, comment?: string) => {
    try {
      await requestsApi.update(reqId, { status: newStatus, comment });
      toast.success('Статус обновлён');
      loadAll();
    } catch (err: any) {
      toast.error(err.response?.data?.detail ?? 'Ошибка');
    }
  };

  const submitDiag = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await requestsApi.createDiagnostic(reqId, {
        ...diagForm,
        request_id: reqId,
        performed_at: new Date().toISOString(),
        estimated_repair_hours: diagForm.estimated_repair_hours ? Number(diagForm.estimated_repair_hours) : null,
      });
      toast.success('Диагностика добавлена');
      setDiagForm({ findings: '', recommended_action: '', estimated_repair_hours: '' });
      loadAll();
    } catch (err: any) {
      toast.error(err.response?.data?.detail ?? 'Ошибка');
    }
  };

  const submitRepair = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await requestsApi.createRepair(reqId, {
        ...repairForm,
        request_id: reqId,
        started_at: new Date().toISOString(),
        labor_hours: repairForm.labor_hours ? Number(repairForm.labor_hours) : null,
      });
      toast.success('Ремонт добавлен');
      setRepairForm({ work_description: '', labor_hours: '', result: '' });
      loadAll();
    } catch (err: any) {
      toast.error(err.response?.data?.detail ?? 'Ошибка');
    }
  };

  const submitReport = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await requestsApi.createReport(reqId, { ...reportForm, request_id: reqId });
      toast.success('Отчёт создан');
      setReportForm({ summary: '', recommendations: '' });
      loadAll();
    } catch (err: any) {
      toast.error(err.response?.data?.detail ?? 'Ошибка');
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
    </div>
  );

  if (!request) return <div className="text-gray-500">Заявка не найдена</div>;

  const canChangeStatus = hasRole('admin', 'dispatcher', 'executor', 'shift_manager');
  const canWork = hasRole('admin', 'executor', 'dispatcher');

  const tabs = [
    { id: 'info', label: 'Информация' },
    { id: 'diagnostic', label: `Диагностика (${diagnostics.length})` },
    { id: 'repair', label: `Ремонт (${repairs.length})` },
    { id: 'report', label: `Отчёты (${reports.length})` },
  ] as const;

  return (
    <div className="space-y-4">
      {/* Back button */}
      <button onClick={() => navigate('/requests')} className="text-sm text-blue-600 hover:text-blue-800">
        ← Назад к заявкам
      </button>

      {/* Header */}
      <div className="bg-white rounded-xl shadow p-5">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="font-mono text-sm text-gray-500">{request.request_number}</span>
              <StatusBadge status={request.status} />
              <PriorityBadge priority={request.priority} />
            </div>
            <h1 className="text-xl font-semibold text-gray-900">{request.title}</h1>
            {request.description && (
              <p className="text-gray-500 text-sm mt-1">{request.description}</p>
            )}
          </div>

          {/* Actions */}
          {canChangeStatus && (
            <div className="flex flex-wrap gap-2">
              {request.status === 'new' && (
                <button
                  onClick={() => updateStatus('assigned')}
                  className="px-3 py-1.5 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg text-sm"
                >
                  Назначить
                </button>
              )}
              {request.status === 'assigned' && (
                <button
                  onClick={() => updateStatus('in_progress')}
                  className="px-3 py-1.5 bg-purple-500 hover:bg-purple-600 text-white rounded-lg text-sm"
                >
                  В работу
                </button>
              )}
              {request.status === 'in_progress' && (
                <>
                  <button
                    onClick={() => updateStatus('waiting_parts')}
                    className="px-3 py-1.5 bg-orange-500 hover:bg-orange-600 text-white rounded-lg text-sm"
                  >
                    Ожидание запчастей
                  </button>
                  <button
                    onClick={() => updateStatus('completed')}
                    className="px-3 py-1.5 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm"
                  >
                    Выполнено
                  </button>
                </>
              )}
              {(request.status === 'completed' || request.status === 'waiting_parts') && (
                <button
                  onClick={() => updateStatus('closed')}
                  className="px-3 py-1.5 bg-gray-500 hover:bg-gray-600 text-white rounded-lg text-sm"
                >
                  Закрыть
                </button>
              )}
              {!['closed', 'cancelled'].includes(request.status) && (
                <button
                  onClick={() => updateStatus('cancelled', 'Отменено')}
                  className="px-3 py-1.5 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm"
                >
                  Отменить
                </button>
              )}
            </div>
          )}
        </div>

        {/* Meta */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 text-sm">
          <div>
            <p className="text-gray-400 text-xs">Оборудование</p>
            <p className="font-medium">{request.equipment?.name ?? `#${request.equipment_id}`}</p>
          </div>
          <div>
            <p className="text-gray-400 text-xs">Инициатор</p>
            <p className="font-medium">{request.initiator?.full_name ?? '—'}</p>
          </div>
          <div>
            <p className="text-gray-400 text-xs">Исполнитель</p>
            <p className="font-medium">{request.executor?.full_name ?? '—'}</p>
          </div>
          <div>
            <p className="text-gray-400 text-xs">Создана</p>
            <p className="font-medium">{format(new Date(request.created_at), 'dd.MM.yyyy HH:mm')}</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow">
        <div className="border-b flex">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-5 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-5">
          {/* Info tab - Status History */}
          {activeTab === 'info' && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-3">История статусов</h3>
              {request.status_history.length === 0 ? (
                <p className="text-gray-400 text-sm">Нет истории</p>
              ) : (
                <div className="space-y-2">
                  {request.status_history.map((h) => (
                    <div key={h.id} className="flex items-start gap-3 text-sm">
                      <div className="mt-0.5 w-2 h-2 rounded-full bg-blue-500 flex-shrink-0 mt-1.5" />
                      <div>
                        <div className="flex items-center gap-2">
                          {h.old_status && <StatusBadge status={h.old_status} size="sm" />}
                          {h.old_status && <span className="text-gray-400">→</span>}
                          <StatusBadge status={h.new_status} size="sm" />
                          <span className="text-gray-400 text-xs">
                            {format(new Date(h.changed_at), 'dd.MM.yyyy HH:mm')}
                          </span>
                          {h.changed_by && (
                            <span className="text-gray-500 text-xs">— {h.changed_by.full_name}</span>
                          )}
                        </div>
                        {h.comment && <p className="text-gray-500 text-xs mt-0.5">{h.comment}</p>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Diagnostic tab */}
          {activeTab === 'diagnostic' && (
            <div className="space-y-4">
              {diagnostics.map((d) => (
                <div key={d.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between text-xs text-gray-400 mb-2">
                    <span>{d.performed_by?.full_name ?? '—'}</span>
                    <span>{format(new Date(d.performed_at), 'dd.MM.yyyy HH:mm')}</span>
                  </div>
                  <p className="text-sm"><strong>Результаты:</strong> {d.findings}</p>
                  {d.recommended_action && (
                    <p className="text-sm mt-1"><strong>Рекомендации:</strong> {d.recommended_action}</p>
                  )}
                  {d.estimated_repair_hours && (
                    <p className="text-sm mt-1 text-gray-500">
                      Оценка времени ремонта: {d.estimated_repair_hours} ч.
                    </p>
                  )}
                </div>
              ))}

              {canWork && (
                <form onSubmit={submitDiag} className="border border-blue-200 rounded-lg p-4 bg-blue-50">
                  <h4 className="text-sm font-semibold mb-3 text-blue-800">Добавить диагностику</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Результаты осмотра *</label>
                      <textarea
                        required
                        rows={3}
                        value={diagForm.findings}
                        onChange={(e) => setDiagForm({ ...diagForm, findings: e.target.value })}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Рекомендации</label>
                      <textarea
                        rows={2}
                        value={diagForm.recommended_action}
                        onChange={(e) => setDiagForm({ ...diagForm, recommended_action: e.target.value })}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Оценка (часов)</label>
                      <input
                        type="number"
                        step="0.5"
                        value={diagForm.estimated_repair_hours}
                        onChange={(e) => setDiagForm({ ...diagForm, estimated_repair_hours: e.target.value })}
                        className="w-32 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm">
                      Сохранить
                    </button>
                  </div>
                </form>
              )}
            </div>
          )}

          {/* Repair tab */}
          {activeTab === 'repair' && (
            <div className="space-y-4">
              {repairs.map((r) => (
                <div key={r.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between text-xs text-gray-400 mb-2">
                    <span>{r.performed_by?.full_name ?? '—'}</span>
                    <span>{format(new Date(r.started_at), 'dd.MM.yyyy HH:mm')}</span>
                  </div>
                  <p className="text-sm"><strong>Работы:</strong> {r.work_description}</p>
                  {r.result && <p className="text-sm mt-1"><strong>Результат:</strong> {r.result}</p>}
                  {r.labor_hours && <p className="text-sm mt-1 text-gray-500">Трудозатраты: {r.labor_hours} ч.</p>}
                </div>
              ))}

              {canWork && (
                <form onSubmit={submitRepair} className="border border-green-200 rounded-lg p-4 bg-green-50">
                  <h4 className="text-sm font-semibold mb-3 text-green-800">Добавить ремонт</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Описание работ *</label>
                      <textarea
                        required
                        rows={3}
                        value={repairForm.work_description}
                        onChange={(e) => setRepairForm({ ...repairForm, work_description: e.target.value })}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Результат</label>
                      <textarea
                        rows={2}
                        value={repairForm.result}
                        onChange={(e) => setRepairForm({ ...repairForm, result: e.target.value })}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Трудозатраты (ч.)</label>
                      <input
                        type="number"
                        step="0.5"
                        value={repairForm.labor_hours}
                        onChange={(e) => setRepairForm({ ...repairForm, labor_hours: e.target.value })}
                        className="w-32 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <button type="submit" className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm">
                      Сохранить
                    </button>
                  </div>
                </form>
              )}
            </div>
          )}

          {/* Reports tab */}
          {activeTab === 'report' && (
            <div className="space-y-4">
              {reports.map((r) => (
                <div key={r.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between text-xs text-gray-400 mb-2">
                    <span>{r.created_by?.full_name ?? '—'}</span>
                    <span>{format(new Date(r.created_at), 'dd.MM.yyyy HH:mm')}</span>
                  </div>
                  <p className="text-sm"><strong>Сводка:</strong> {r.summary}</p>
                  {r.recommendations && (
                    <p className="text-sm mt-1"><strong>Рекомендации:</strong> {r.recommendations}</p>
                  )}
                </div>
              ))}

              {canWork && request.status === 'completed' && (
                <form onSubmit={submitReport} className="border border-gray-200 rounded-lg p-4">
                  <h4 className="text-sm font-semibold mb-3">Создать отчёт</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Сводка *</label>
                      <textarea
                        required
                        rows={3}
                        value={reportForm.summary}
                        onChange={(e) => setReportForm({ ...reportForm, summary: e.target.value })}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Рекомендации</label>
                      <textarea
                        rows={2}
                        value={reportForm.recommendations}
                        onChange={(e) => setReportForm({ ...reportForm, recommendations: e.target.value })}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <button type="submit" className="px-4 py-2 bg-gray-700 hover:bg-gray-800 text-white rounded-lg text-sm">
                      Создать отчёт
                    </button>
                  </div>
                </form>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
