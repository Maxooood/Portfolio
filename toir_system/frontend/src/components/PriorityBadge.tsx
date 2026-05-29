import React from 'react';

const priorityConfig: Record<string, { label: string; className: string }> = {
  low: { label: 'Низкий', className: 'bg-gray-100 text-gray-700' },
  medium: { label: 'Средний', className: 'bg-blue-100 text-blue-700' },
  high: { label: 'Высокий', className: 'bg-orange-100 text-orange-800' },
  critical: { label: 'Критический', className: 'bg-red-100 text-red-800' },
};

interface PriorityBadgeProps {
  priority: string;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({ priority }) => {
  const config = priorityConfig[priority] ?? { label: priority, className: 'bg-gray-100 text-gray-700' };
  return (
    <span className={`inline-flex items-center text-xs font-medium rounded-full px-2.5 py-1 ${config.className}`}>
      {config.label}
    </span>
  );
};
