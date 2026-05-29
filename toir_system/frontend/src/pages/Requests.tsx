import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { requestsApi } from '../api/requests';
import { equipmentApi } from '../api/equipment';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';
import { DataTable } from '../components/DataTable';
import { useAuthStore } from '../store/auth';
import type { Request, Equipment, FaultType } from '../types';
import { format } from 'date-fns';

const emptyForm = {
  title: '',
  description: '',
  priority: 'medium',
  equipment_id: '',
  fault_type_id: '',
  request_type: 'unplanned',
};

export const Requests: React.FC = () => {
  const navigate = useNavigate();
  const [requests, setRequests] = useState<Request[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [faultTypes, setFaultTypes] = useState<FaultType[]>([]);
  const { hasRole } = useAuthStore();

  const canCreate = hasRole('admin', 'manager', 'dispatcher', 'shift_manager');

  const load = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (statusFilter) params.status = statusFilter;
      if (priorityFilter) params.priority = priorityFilter;
      const data = await requestsApi.list(params);
      setRequests(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [statusFilter, priorityFilter]);

  useEffect(() => {
    equipmentApi.list().then(setEquipment);
    requestsApi.listFaultTypes().then(setFaultTypes);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await requestsApi.create({
        ...form,
        equipment_id: Number(form.equipment_id),
        fault_type_id: form.fault_type_id ? Number(form.fault_type_id) : undefined,
      });
      toast.success('Заявка создана');
      setShowModal(false);
      setForm(emptyForm);
      load();
    } catch (err: any) {
      toast.error(err.response?.data?.detail ?? 'Ошибка создания заявки');
    }
  };

  const columns = [
    { key: 'request_number', header: '№ Заявки', className: 'font-mono text-xs' },
    { key: 'title', header: 'Заголовок' },
    {
      key: 'equipment',
      header: 'Оборудование',
      render: (r: Request) => r.equipment?.name ?? `#${r.equipment_id}`,
    },
    {
      key: 'priority',
      header: 'Приоритет',
      render: (r: Request) => <PriorityBadge priority={r.priority} />,
    },
    {
      key: 'status',
      header: 'Статус',
      render: (r: Request) => <StatusBadge status={r.status} />,
    },
    {
      key: 'executor',
      header: 'Исполнитель',
      render: (r: Request) => r.executor?.full_name ?? '—',
    },
    {
      key: 'created_at',
      header: 'Создана',
      render: (r: Request) => format(new Date(r.created_at), 'dd.MM.yy HH:mm'),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Все статусы</option>
          <option value="new">Новая</option>
          <option value="assigned">Назначена</option>
          <option value="in_progress">В работе</option>
          <option value="waiting_parts">Ожидание запчастей</option>
          <option value="completed">Выполнена</option>
          <option value="closed">Закрыта</option>
          <option value="cancelled">Отменена</option>
        </select>

        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Все приоритеты</option>
          <option value="low">Низкий</option>
          <option value="medium">Средний</option>
          <option value="high">Высокий</option>
          <option value="critical">Критический</option>
        </select>

        {canCreate && (
          <button
            onClick={() => setShowModal(true)}
            className="ml-auto bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
          >
            + Создать заявку
          </button>
        )}
      </div>

      <div className="bg-white rounded-xl shadow">
        <DataTable
          columns={columns}
          data={requests}
          loading={loading}
          onRowClick={(r) => navigate(`/requests/${r.id}`)}
          emptyMessage="Заявки не найдены"
        />
      </div>

      {/* Create modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
            <div className="p-6">
              <h2 className="text-lg font-semibold mb-4">Новая заявка</h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Заголовок *</label>
                  <input
                    required
                    value={form.title}
                    onChange={(e) => setForm({ ...form, title: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Описание</label>
                  <textarea
                    rows={3}
                    value={form.description}
                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Оборудование *</label>
                    <select
                      required
                      value={form.equipment_id}
                      onChange={(e) => setForm({ ...form, equipment_id: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">— выберите —</option>
                      {equipment.map((eq) => (
                        <option key={eq.id} value={eq.id}>{eq.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Приоритет</label>
                    <select
                      value={form.priority}
                      onChange={(e) => setForm({ ...form, priority: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="low">Низкий</option>
                      <option value="medium">Средний</option>
                      <option value="high">Высокий</option>
                      <option value="critical">Критический</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Вид неисправности</label>
                  <select
                    value={form.fault_type_id}
                    onChange={(e) => setForm({ ...form, fault_type_id: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">— не указано —</option>
                    {faultTypes.map((ft) => (
                      <option key={ft.id} value={ft.id}>{ft.name}</option>
                    ))}
                  </select>
                </div>

                <div className="flex gap-3 justify-end pt-2">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
                  >
                    Отмена
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium"
                  >
                    Создать
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
