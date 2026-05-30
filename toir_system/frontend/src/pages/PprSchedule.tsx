import React, { useEffect, useState } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, getDay } from 'date-fns';
import { ru } from 'date-fns/locale';
import toast from 'react-hot-toast';
import { pprApi } from '../api/ppr';
import { StatusBadge } from '../components/StatusBadge';
import { useAuthStore } from '../store/auth';
import type { PprSchedule, PprTask } from '../types';

const taskStatusColors: Record<string, string> = {
  planned: 'bg-blue-100 border-blue-300 text-blue-800',
  in_progress: 'bg-purple-100 border-purple-300 text-purple-800',
  completed: 'bg-green-100 border-green-300 text-green-800',
  overdue: 'bg-red-100 border-red-300 text-red-800',
  cancelled: 'bg-gray-100 border-gray-300 text-gray-500',
};

export const PprSchedulePage: React.FC = () => {
  const [schedules, setSchedules] = useState<PprSchedule[]>([]);
  const [selectedSchedule, setSelectedSchedule] = useState<PprSchedule | null>(null);
  const [tasks, setTasks] = useState<PprTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [genYear, setGenYear] = useState(new Date().getFullYear());
  const [genMonth, setGenMonth] = useState(new Date().getMonth() + 1);
  const { hasRole } = useAuthStore();

  const canGenerate = hasRole('admin', 'ppr_engineer');
  const canApprove = hasRole('admin', 'dispatcher');

  const loadSchedules = async () => {
    setLoading(true);
    try {
      const data = await pprApi.listSchedules();
      setSchedules(data);
      if (data.length > 0 && !selectedSchedule) {
        setSelectedSchedule(data[0]);
      }
    } finally {
      setLoading(false);
    }
  };

  const loadTasks = async (scheduleId: number) => {
    const data = await pprApi.getScheduleTasks(scheduleId);
    setTasks(data);
  };

  useEffect(() => { loadSchedules(); }, []);

  useEffect(() => {
    if (selectedSchedule) loadTasks(selectedSchedule.id);
    else setTasks([]);
  }, [selectedSchedule]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const schedule = await pprApi.generateSchedule(genYear, genMonth);
      toast.success('График ППР сгенерирован');
      await loadSchedules();
      setSelectedSchedule(schedule);
    } catch (err: any) {
      toast.error(err.response?.data?.detail ?? 'Ошибка генерации');
    } finally {
      setGenerating(false);
    }
  };

  const handleApprove = async () => {
    if (!selectedSchedule) return;
    try {
      await pprApi.approveSchedule(selectedSchedule.id);
      toast.success('График утверждён');
      loadSchedules();
    } catch {
      toast.error('Ошибка утверждения');
    }
  };

  const handleTaskStatusChange = async (task: PprTask, newStatus: string) => {
    try {
      await pprApi.updateTaskStatus(task.id, newStatus);
      if (selectedSchedule) loadTasks(selectedSchedule.id);
    } catch {
      toast.error('Ошибка обновления статуса');
    }
  };

  const handleCreateRequest = async (task: PprTask) => {
    try {
      const result = await pprApi.createRequestFromTask(task.id);
      toast.success(`Заявка ${result.request_number} создана`);
      if (selectedSchedule) loadTasks(selectedSchedule.id);
    } catch (err: any) {
      toast.error(err.response?.data?.detail ?? 'Ошибка создания заявки');
    }
  };

  // Group tasks by day for calendar view
  const tasksByDay: Record<string, PprTask[]> = {};
  tasks.forEach((t) => {
    const day = t.planned_date.substring(0, 10);
    if (!tasksByDay[day]) tasksByDay[day] = [];
    tasksByDay[day].push(t);
  });

  // Calendar grid
  const calendarDays = selectedSchedule
    ? eachDayOfInterval({
        start: startOfMonth(new Date(selectedSchedule.year, selectedSchedule.month - 1)),
        end: endOfMonth(new Date(selectedSchedule.year, selectedSchedule.month - 1)),
      })
    : [];

  const firstDayOfWeek = calendarDays.length > 0 ? (getDay(calendarDays[0]) + 6) % 7 : 0; // Mon=0

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="bg-white rounded-xl shadow p-4 flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-600">График:</label>
          <select
            value={selectedSchedule?.id ?? ''}
            onChange={(e) => {
              const s = schedules.find((s) => s.id === Number(e.target.value));
              setSelectedSchedule(s ?? null);
            }}
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">— выберите —</option>
            {schedules.map((s) => (
              <option key={s.id} value={s.id}>
                {s.year}-{String(s.month).padStart(2, '0')}{s.is_approved ? ' ✓' : ''}
              </option>
            ))}
          </select>
        </div>

        {selectedSchedule && !selectedSchedule.is_approved && canApprove && (
          <button
            onClick={handleApprove}
            className="px-4 py-1.5 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm"
          >
            Утвердить
          </button>
        )}

        {canGenerate && (
          <div className="flex items-center gap-2 ml-auto">
            <select
              value={genYear}
              onChange={(e) => setGenYear(Number(e.target.value))}
              className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
            >
              {[2024, 2025, 2026, 2027].map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
            <select
              value={genMonth}
              onChange={(e) => setGenMonth(Number(e.target.value))}
              className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
            >
              {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                <option key={m} value={m}>
                  {format(new Date(2024, m - 1), 'LLLL', { locale: ru })}
                </option>
              ))}
            </select>
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white rounded-lg text-sm font-medium"
            >
              {generating ? 'Генерация...' : 'Сгенерировать'}
            </button>
          </div>
        )}
      </div>

      {selectedSchedule && (
        <div className="flex items-center gap-3">
          <h2 className="text-base font-semibold text-gray-700">
            График на {format(new Date(selectedSchedule.year, selectedSchedule.month - 1), 'LLLL yyyy', { locale: ru })}
          </h2>
          <StatusBadge status={selectedSchedule.is_approved ? 'completed' : 'planned'} />
          <span className="text-sm text-gray-500">
            Задач: {tasks.length}
          </span>
        </div>
      )}

      {/* Calendar */}
      {calendarDays.length > 0 && (
        <div className="bg-white rounded-xl shadow p-4">
          <div className="grid grid-cols-7 gap-1 mb-2">
            {['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'].map((d) => (
              <div key={d} className="text-xs font-medium text-gray-400 text-center py-1">{d}</div>
            ))}
          </div>
          <div className="grid grid-cols-7 gap-1">
            {/* Empty cells before first day */}
            {Array.from({ length: firstDayOfWeek }).map((_, i) => (
              <div key={`empty-${i}`} />
            ))}
            {calendarDays.map((day) => {
              const key = format(day, 'yyyy-MM-dd');
              const dayTasks = tasksByDay[key] ?? [];
              const isToday = key === format(new Date(), 'yyyy-MM-dd');
              return (
                <div
                  key={key}
                  className={`min-h-16 border rounded-lg p-1 ${
                    isToday ? 'border-blue-400 bg-blue-50' : 'border-gray-100'
                  }`}
                >
                  <span className={`text-xs font-medium ${isToday ? 'text-blue-600' : 'text-gray-500'}`}>
                    {format(day, 'd')}
                  </span>
                  <div className="mt-0.5 space-y-0.5">
                    {dayTasks.slice(0, 3).map((t) => (
                      <div
                        key={t.id}
                        title={t.equipment?.name ?? `EQ #${t.equipment_id}`}
                        className={`text-xs px-1 py-0.5 rounded border truncate cursor-default ${taskStatusColors[t.status]}`}
                      >
                        {t.equipment?.name ?? `EQ #${t.equipment_id}`}
                      </div>
                    ))}
                    {dayTasks.length > 3 && (
                      <div className="text-xs text-gray-400 pl-1">+{dayTasks.length - 3}</div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tasks table */}
      {tasks.length > 0 && (
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <div className="px-4 py-3 border-b">
            <h3 className="text-sm font-semibold text-gray-700">Список задач ППР</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  {['Дата', 'Оборудование', 'Вид ТО', 'Статус', 'Действия'].map((h) => (
                    <th key={h} className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {tasks.map((task) => (
                  <tr key={task.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-gray-600 text-xs">
                      {format(new Date(task.planned_date), 'dd.MM.yyyy')}
                    </td>
                    <td className="px-4 py-2">{task.equipment?.name ?? `#${task.equipment_id}`}</td>
                    <td className="px-4 py-2 text-gray-600 text-xs">
                      {task.norm?.description ?? task.norm?.norm_type ?? '—'}
                    </td>
                    <td className="px-4 py-2"><StatusBadge status={task.status} /></td>
                    <td className="px-4 py-2">
                      <div className="flex gap-2">
                        {task.status === 'planned' && (
                          <>
                            <button
                              onClick={() => handleTaskStatusChange(task, 'completed')}
                              className="text-xs text-green-600 hover:text-green-800"
                            >
                              Выполнено
                            </button>
                            {!task.request_id && (
                              <button
                                onClick={() => handleCreateRequest(task)}
                                className="text-xs text-blue-600 hover:text-blue-800"
                              >
                                Создать заявку
                              </button>
                            )}
                            <button
                              onClick={() => handleTaskStatusChange(task, 'cancelled')}
                              className="text-xs text-red-500 hover:text-red-700"
                            >
                              Отменить
                            </button>
                          </>
                        )}
                        {task.request_id && (
                          <span className="text-xs text-gray-500">Заявка #{task.request_id}</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center h-40">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      )}

      {!loading && schedules.length === 0 && (
        <div className="bg-white rounded-xl shadow p-10 text-center text-gray-400">
          <p className="text-lg">Графики ППР не найдены</p>
          {canGenerate && <p className="text-sm mt-1">Сгенерируйте первый график выше</p>}
        </div>
      )}
    </div>
  );
};
