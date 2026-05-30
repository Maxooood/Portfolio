import React from 'react';

const statusConfig: Record<string, { label: string; className: string }> = {
  // Request statuses
  new: { label: 'Новая', className: 'bg-blue-100 text-blue-800' },
  assigned: { label: 'Назначена', className: 'bg-yellow-100 text-yellow-800' },
  in_progress: { label: 'В работе', className: 'bg-purple-100 text-purple-800' },
  waiting_parts: { label: 'Ожидание запчастей', className: 'bg-orange-100 text-orange-800' },
  completed: { label: 'Выполнена', className: 'bg-green-100 text-green-800' },
  closed: { label: 'Закрыта', className: 'bg-gray-100 text-gray-800' },
  cancelled: { label: 'Отменена', className: 'bg-red-100 text-red-800' },
  // PPR statuses
  planned: { label: 'Запланировано', className: 'bg-blue-100 text-blue-800' },
  overdue: { label: 'Просрочено', className: 'bg-red-100 text-red-800' },
  // Equipment statuses
  operational: { label: 'В работе', className: 'bg-green-100 text-green-800' },
  under_maintenance: { label: 'ТО', className: 'bg-yellow-100 text-yellow-800' },
  broken: { label: 'Неисправно', className: 'bg-red-100 text-red-800' },
  decommissioned: { label: 'Списано', className: 'bg-gray-100 text-gray-800' },
};

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const config = statusConfig[status] ?? { label: status, className: 'bg-gray-100 text-gray-700' };
  const sizeClass = size === 'sm' ? 'text-xs px-1.5 py-0.5' : 'text-xs px-2.5 py-1';
  return (
    <span className={`inline-flex items-center font-medium rounded-full ${sizeClass} ${config.className}`}>
      {config.label}
    </span>
  );
};
