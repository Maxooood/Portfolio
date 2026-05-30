import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/auth';

const roleLabels: Record<string, string> = {
  admin: 'Администратор',
  manager: 'Менеджер',
  dispatcher: 'Диспетчер',
  shift_manager: 'Начальник смены',
  executor: 'Исполнитель',
  ppr_engineer: 'ППР-инженер',
};

const navItems = [
  { path: '/', label: 'Дашборд', icon: '📊', roles: null },
  { path: '/equipment', label: 'Оборудование', icon: '🔧', roles: null },
  { path: '/ppr', label: 'График ППР', icon: '📅', roles: ['admin', 'manager', 'dispatcher', 'ppr_engineer'] },
  { path: '/requests', label: 'Заявки', icon: '📋', roles: null },
  { path: '/analytics', label: 'Аналитика', icon: '📈', roles: ['admin', 'manager', 'dispatcher'] },
  { path: '/admin', label: 'Администрирование', icon: '⚙️', roles: ['admin', 'manager'] },
];

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuthStore();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const visibleItems = navItems.filter(
    (item) => !item.roles || (user && item.roles.includes(user.role))
  );

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-16'
        } bg-gray-900 text-white flex flex-col transition-all duration-300`}
      >
        {/* Logo */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          {sidebarOpen && (
            <span className="font-bold text-lg text-blue-400">ИС ТОиР</span>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1 rounded hover:bg-gray-700 text-gray-400"
          >
            {sidebarOpen ? '◀' : '▶'}
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-4">
          {visibleItems.map((item) => {
            const active = location.pathname === item.path ||
              (item.path !== '/' && location.pathname.startsWith(item.path));
            return (
              <Link
                key={item.path}
                to={item.path}
                title={!sidebarOpen ? item.label : undefined}
                className={`flex items-center px-4 py-3 text-sm transition-colors ${
                  active
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                {sidebarOpen && <span className="ml-3">{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* User info */}
        <div className="border-t border-gray-700 p-4">
          {sidebarOpen ? (
            <div>
              <p className="text-sm font-medium text-white truncate">{user?.full_name}</p>
              <p className="text-xs text-gray-400">{user ? roleLabels[user.role] : ''}</p>
              <button
                onClick={handleLogout}
                className="mt-2 text-xs text-red-400 hover:text-red-300"
              >
                Выйти
              </button>
            </div>
          ) : (
            <button
              onClick={handleLogout}
              title="Выйти"
              className="text-red-400 hover:text-red-300 text-lg"
            >
              🚪
            </button>
          )}
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm px-6 py-3 flex items-center justify-between">
          <h1 className="text-lg font-semibold text-gray-800">
            {visibleItems.find((i) =>
              i.path === '/'
                ? location.pathname === '/'
                : location.pathname.startsWith(i.path)
            )?.label ?? 'ИС ТОиР'}
          </h1>
          <div className="text-sm text-gray-500">
            {user?.employee_number} — {user?.department}
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
};
