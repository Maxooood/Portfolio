import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { equipmentApi } from '../api/equipment';
import { StatusBadge } from '../components/StatusBadge';
import { DataTable } from '../components/DataTable';
import { useAuthStore } from '../store/auth';
import type { Equipment } from '../types';

const emptyForm = {
  name: '',
  inventory_number: '',
  equipment_type: '',
  location: '',
  department: '',
  manufacturer: '',
  model: '',
  year_of_manufacture: '',
  status: 'operational',
};

export const EquipmentPage: React.FC = () => {
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editItem, setEditItem] = useState<Equipment | null>(null);
  const [form, setForm] = useState<typeof emptyForm>(emptyForm);
  const [filterStatus, setFilterStatus] = useState('');
  const { hasRole } = useAuthStore();

  const canEdit = hasRole('admin', 'manager', 'dispatcher');

  const load = async () => {
    setLoading(true);
    try {
      const data = await equipmentApi.list(filterStatus ? { status: filterStatus } : undefined);
      setEquipment(data);
    } catch {
      toast.error('Ошибка загрузки оборудования');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [filterStatus]);

  const openCreate = () => {
    setEditItem(null);
    setForm(emptyForm);
    setShowModal(true);
  };

  const openEdit = (item: Equipment) => {
    setEditItem(item);
    setForm({
      name: item.name,
      inventory_number: item.inventory_number,
      equipment_type: item.equipment_type ?? '',
      location: item.location ?? '',
      department: item.department ?? '',
      manufacturer: item.manufacturer ?? '',
      model: item.model ?? '',
      year_of_manufacture: item.year_of_manufacture ? String(item.year_of_manufacture) : '',
      status: item.status,
    });
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: any = {
        ...form,
        year_of_manufacture: form.year_of_manufacture ? Number(form.year_of_manufacture) : null,
      };
      if (editItem) {
        await equipmentApi.update(editItem.id, payload);
        toast.success('Оборудование обновлено');
      } else {
        await equipmentApi.create(payload);
        toast.success('Оборудование добавлено');
      }
      setShowModal(false);
      load();
    } catch (err: any) {
      toast.error(err.response?.data?.detail ?? 'Ошибка сохранения');
    }
  };

  const columns = [
    { key: 'inventory_number', header: 'Инв. номер', className: 'font-mono text-xs' },
    { key: 'name', header: 'Наименование' },
    { key: 'equipment_type', header: 'Тип', render: (i: Equipment) => i.equipment_type ?? '—' },
    { key: 'location', header: 'Местонахождение', render: (i: Equipment) => i.location ?? '—' },
    { key: 'department', header: 'Подразделение', render: (i: Equipment) => i.department ?? '—' },
    { key: 'status', header: 'Статус', render: (i: Equipment) => <StatusBadge status={i.status} /> },
    ...(canEdit ? [{
      key: 'actions',
      header: '',
      render: (i: Equipment) => (
        <button
          onClick={(e) => { e.stopPropagation(); openEdit(i); }}
          className="text-blue-600 hover:text-blue-800 text-xs"
        >
          Изменить
        </button>
      ),
    }] : []),
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Все статусы</option>
            <option value="operational">В работе</option>
            <option value="under_maintenance">ТО</option>
            <option value="broken">Неисправно</option>
            <option value="decommissioned">Списано</option>
          </select>
        </div>
        {canEdit && (
          <button
            onClick={openCreate}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
          >
            + Добавить оборудование
          </button>
        )}
      </div>

      <div className="bg-white rounded-xl shadow">
        <DataTable columns={columns} data={equipment} loading={loading} emptyMessage="Оборудование не найдено" />
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-lg font-semibold mb-4">
                {editItem ? 'Редактировать оборудование' : 'Добавить оборудование'}
              </h2>
              <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
                {[
                  ['name', 'Наименование', 'text', true],
                  ['inventory_number', 'Инвентарный номер', 'text', true],
                  ['equipment_type', 'Тип оборудования', 'text', false],
                  ['location', 'Местонахождение', 'text', false],
                  ['department', 'Подразделение', 'text', false],
                  ['manufacturer', 'Производитель', 'text', false],
                  ['model', 'Модель', 'text', false],
                  ['year_of_manufacture', 'Год выпуска', 'number', false],
                ].map(([key, label, type, required]) => (
                  <div key={key as string}>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{label as string}</label>
                    <input
                      type={type as string}
                      required={required as boolean}
                      value={(form as any)[key as string]}
                      onChange={(e) => setForm({ ...form, [key as string]: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                ))}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Статус</label>
                  <select
                    value={form.status}
                    onChange={(e) => setForm({ ...form, status: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="operational">В работе</option>
                    <option value="under_maintenance">ТО</option>
                    <option value="broken">Неисправно</option>
                    <option value="decommissioned">Списано</option>
                  </select>
                </div>
                <div className="col-span-2 flex gap-3 justify-end mt-2">
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
                    Сохранить
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
