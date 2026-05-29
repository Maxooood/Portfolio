import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import apiClient from '../api/client';
import type { User, FaultType, AuxiliaryService } from '../types';
import { DataTable } from '../components/DataTable';
import { useAuthStore } from '../store/auth';
import { format } from 'date-fns';

const ROLE_LABELS: Record<string, string> = {
  admin: 'Администратор',
  manager: 'Менеджер',
  dispatcher: 'Диспетчер',
  shift_manager: 'Нач. смены',
  executor: 'Исполнитель',
  ppr_engineer: 'ППР-инженер',
};

const tabs = ['Пользователи', 'Виды неисправностей', 'Службы', 'Журнал аудита'] as const;
type Tab = typeof tabs[number];

export const Admin: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('Пользователи');
  const [users, setUsers] = useState<User[]>([]);
  const [faultTypes, setFaultTypes] = useState<FaultType[]>([]);
  const [services, setServices] = useState<AuxiliaryService[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const { hasRole } = useAuthStore();

  // Create user form
  const [showUserModal, setShowUserModal] = useState(false);
  const [userForm, setUserForm] = useState({
    employee_number: '', full_name: '', email: '',
    role: 'executor', department: '', phone: '', password: '',
  });

  // FaultType form
  const [ftForm, setFtForm] = useState({ name: '', description: '' });

  // Service form
  const [svcForm, setSvcForm] = useState({ name: '', description: '' });

  const loadTab = async (tab: Tab) => {
    setLoading(true);
    try {
      if (tab === 'Пользователи') {
        const res = await apiClient.get('/users');
        setUsers(res.data);
      } else if (tab === 'Виды неисправностей') {
        const res = await apiClient.get('/fault-types');
        setFaultTypes(res.data);
      } else if (tab === 'Службы') {
        const res = await apiClient.get('/services');
        setServices(res.data);
      } else if (tab === 'Журнал аудита') {
        const res = await apiClient.get('/admin/audit-logs');
        setAuditLogs(res.data);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadTab(activeTab); }, [activeTab]);

  const createUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/users', userForm);
      toast.success('Пользователь создан');
      setShowUserModal(false);
      setUserForm({ employee_number: '', full_name: '', email: '', role: 'executor', department: '', phone: '', password: '' });
      loadTab('Пользователи');
    } catch (err: any) {
      toast.error(err.response?.data?.detail ?? 'Ошибка');
    }
  };

  const toggleUserActive = async (user: User) => {
    try {
      await apiClient.patch(`/users/${user.id}`, { is_active: !user.is_active });
      toast.success(user.is_active ? 'Пользователь деактивирован' : 'Пользователь активирован');
      loadTab('Пользователи');
    } catch {
      toast.error('Ошибка');
    }
  };

  const createFaultType = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/fault-types', ftForm);
      toast.success('Вид неисправности добавлен');
      setFtForm({ name: '', description: '' });
      loadTab('Виды неисправностей');
    } catch (err: any) {
      toast.error(err.response?.data?.detail ?? 'Ошибка');
    }
  };

  const createService = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/services', svcForm);
      toast.success('Служба добавлена');
      setSvcForm({ name: '', description: '' });
      loadTab('Службы');
    } catch (err: any) {
      toast.error(err.response?.data?.detail ?? 'Ошибка');
    }
  };

  return (
    <div className="space-y-4">
      {/* Tabs */}
      <div className="bg-white rounded-xl shadow">
        <div className="border-b flex overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-5 py-3 text-sm font-medium whitespace-nowrap transition-colors ${
                activeTab === tab
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="p-5">
          {/* Users */}
          {activeTab === 'Пользователи' && (
            <div className="space-y-4">
              {hasRole('admin') && (
                <button
                  onClick={() => setShowUserModal(true)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm"
                >
                  + Добавить пользователя
                </button>
              )}
              <DataTable
                columns={[
                  { key: 'employee_number', header: 'Таб. номер', className: 'font-mono text-xs' },
                  { key: 'full_name', header: 'ФИО' },
                  { key: 'email', header: 'Email' },
                  { key: 'role', header: 'Роль', render: (u: User) => ROLE_LABELS[u.role] ?? u.role },
                  { key: 'department', header: 'Подразделение', render: (u: User) => u.department ?? '—' },
                  {
                    key: 'is_active',
                    header: 'Активен',
                    render: (u: User) => (
                      <span className={`text-xs font-medium ${u.is_active ? 'text-green-600' : 'text-red-500'}`}>
                        {u.is_active ? 'Да' : 'Нет'}
                      </span>
                    ),
                  },
                  ...(hasRole('admin') ? [{
                    key: 'actions',
                    header: '',
                    render: (u: User) => (
                      <button
                        onClick={() => toggleUserActive(u)}
                        className={`text-xs ${u.is_active ? 'text-red-500 hover:text-red-700' : 'text-green-600 hover:text-green-800'}`}
                      >
                        {u.is_active ? 'Деактивировать' : 'Активировать'}
                      </button>
                    ),
                  }] : []),
                ]}
                data={users}
                loading={loading}
              />
            </div>
          )}

          {/* Fault types */}
          {activeTab === 'Виды неисправностей' && (
            <div className="space-y-4">
              {hasRole('admin', 'dispatcher') && (
                <form onSubmit={createFaultType} className="flex gap-3 items-end">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Название</label>
                    <input
                      required
                      value={ftForm.name}
                      onChange={(e) => setFtForm({ ...ftForm, name: e.target.value })}
                      className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                      placeholder="Новый вид"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Описание</label>
                    <input
                      value={ftForm.description}
                      onChange={(e) => setFtForm({ ...ftForm, description: e.target.value })}
                      className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                      placeholder="Описание"
                    />
                  </div>
                  <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm">
                    + Добавить
                  </button>
                </form>
              )}
              <DataTable
                columns={[
                  { key: 'name', header: 'Название' },
                  { key: 'description', header: 'Описание', render: (f: FaultType) => f.description ?? '—' },
                  { key: 'is_active', header: 'Активен', render: (f: FaultType) => f.is_active ? 'Да' : 'Нет' },
                ]}
                data={faultTypes}
                loading={loading}
              />
            </div>
          )}

          {/* Services */}
          {activeTab === 'Службы' && (
            <div className="space-y-4">
              {hasRole('admin', 'dispatcher') && (
                <form onSubmit={createService} className="flex gap-3 items-end">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Название службы</label>
                    <input
                      required
                      value={svcForm.name}
                      onChange={(e) => setSvcForm({ ...svcForm, name: e.target.value })}
                      className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Описание</label>
                    <input
                      value={svcForm.description}
                      onChange={(e) => setSvcForm({ ...svcForm, description: e.target.value })}
                      className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    />
                  </div>
                  <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm">
                    + Добавить
                  </button>
                </form>
              )}
              <DataTable
                columns={[
                  { key: 'name', header: 'Название' },
                  { key: 'description', header: 'Описание', render: (s: AuxiliaryService) => s.description ?? '—' },
                  { key: 'is_active', header: 'Активна', render: (s: AuxiliaryService) => s.is_active ? 'Да' : 'Нет' },
                ]}
                data={services}
                loading={loading}
              />
            </div>
          )}

          {/* Audit log */}
          {activeTab === 'Журнал аудита' && (
            <DataTable
              columns={[
                { key: 'created_at', header: 'Время', render: (l: any) => format(new Date(l.created_at), 'dd.MM.yy HH:mm') },
                { key: 'user', header: 'Пользователь', render: (l: any) => l.user?.full_name ?? 'Система' },
                { key: 'action', header: 'Действие' },
                { key: 'entity_type', header: 'Объект', render: (l: any) => l.entity_type ?? '—' },
              ]}
              data={auditLogs}
              loading={loading}
              emptyMessage="Журнал пуст"
            />
          )}
        </div>
      </div>

      {/* User create modal */}
      {showUserModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
            <div className="p-6">
              <h2 className="text-lg font-semibold mb-4">Новый пользователь</h2>
              <form onSubmit={createUser} className="grid grid-cols-2 gap-4">
                {[
                  ['employee_number', 'Таб. номер', 'text'],
                  ['full_name', 'ФИО', 'text'],
                  ['email', 'Email', 'email'],
                  ['password', 'Пароль', 'password'],
                  ['department', 'Подразделение', 'text'],
                  ['phone', 'Телефон', 'text'],
                ].map(([key, label, type]) => (
                  <div key={key}>
                    <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
                    <input
                      type={type}
                      required={['employee_number', 'full_name', 'email', 'password'].includes(key)}
                      value={(userForm as any)[key]}
                      onChange={(e) => setUserForm({ ...userForm, [key]: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    />
                  </div>
                ))}
                <div className="col-span-2">
                  <label className="block text-xs font-medium text-gray-600 mb-1">Роль</label>
                  <select
                    value={userForm.role}
                    onChange={(e) => setUserForm({ ...userForm, role: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  >
                    {Object.entries(ROLE_LABELS).map(([val, label]) => (
                      <option key={val} value={val}>{label}</option>
                    ))}
                  </select>
                </div>
                <div className="col-span-2 flex gap-3 justify-end">
                  <button type="button" onClick={() => setShowUserModal(false)} className="px-4 py-2 border border-gray-300 rounded-lg text-sm">
                    Отмена
                  </button>
                  <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm">
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
