import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

interface SidebarProps {
  isOpen: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen }) => {
  const location = useLocation();
  const { currentUser, logout } = useAuth();

  const isAdministrador = currentUser?.role === 'Administrador';

  const handleLogout = () => {
    logout();
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <aside className={`w-72 bg-white border-r border-slate-200 flex flex-col flex-shrink-0 transition-all duration-300 ease-in-out shadow-modern-sm ${isOpen ? '' : 'w-0 overflow-hidden'} md:relative md:top-0 md:left-0 md:h-screen md:z-50 md:shadow-modern ${!isOpen ? 'md:transform md:-translate-x-full' : ''}`}>
      <div className="p-8 flex items-center gap-4 border-b border-slate-100">
        <div className="bg-gradient-to-br from-teal-500 to-teal-600 rounded-xl p-3 flex items-center justify-center shadow-modern-sm">
          <i className="fas fa-shield-alt text-white text-lg"></i>
        </div>
        <div>
          <h1 className="text-xl font-semibold text-slate-800 m-0">ISIRT</h1>
          <p className="text-xs text-slate-500 m-0 mt-1">Sistema de Incidentes</p>
        </div>
      </div>
      <nav className="flex-1 p-6 flex flex-col gap-3">
        {isAdministrador && (
          <Link to="/dashboard" className={`group flex items-center px-4 py-3 text-slate-600 font-medium no-underline rounded-lg transition-all duration-200 hover:bg-slate-50 hover:text-teal-600 hover:shadow-modern-xs ${isActive('/dashboard') ? 'bg-teal-50 text-teal-600 shadow-modern-xs border border-teal-100' : ''}`}>
            <i className="fas fa-chart-line mr-4 w-5 text-center text-lg group-hover:scale-110 transition-transform duration-200"></i>
            <span className="text-sm">Dashboard</span>
          </Link>
        )}
        <Link to="/report" className={`group flex items-center px-4 py-3 text-slate-600 font-medium no-underline rounded-lg transition-all duration-200 hover:bg-slate-50 hover:text-teal-600 hover:shadow-modern-xs ${isActive('/report') ? 'bg-teal-50 text-teal-600 shadow-modern-xs border border-teal-100' : ''}`}>
          <i className="fas fa-plus-circle mr-4 w-5 text-center text-lg group-hover:scale-110 transition-transform duration-200"></i>
          <span className="text-sm">Reportar Incidente</span>
        </Link>
        {isAdministrador && (
          <Link to="/users" className={`group flex items-center px-4 py-3 text-slate-600 font-medium no-underline rounded-lg transition-all duration-200 hover:bg-slate-50 hover:text-teal-600 hover:shadow-modern-xs ${isActive('/users') ? 'bg-teal-50 text-teal-600 shadow-modern-xs border border-teal-100' : ''}`}>
            <i className="fas fa-users mr-4 w-5 text-center text-lg group-hover:scale-110 transition-transform duration-200"></i>
            <span className="text-sm">Gestionar Usuarios</span>
          </Link>
        )}
        {isAdministrador && (
          <Link to="/groups" className={`group flex items-center px-4 py-3 text-slate-600 font-medium no-underline rounded-lg transition-all duration-200 hover:bg-slate-50 hover:text-teal-600 hover:shadow-modern-xs ${isActive('/groups') ? 'bg-teal-50 text-teal-600 shadow-modern-xs border border-teal-100' : ''}`}>
            <i className="fas fa-user-friends mr-4 w-5 text-center text-lg group-hover:scale-110 transition-transform duration-200"></i>
            <span className="text-sm">Gestionar Grupos</span>
          </Link>
        )}
        {isAdministrador && (
          <Link to="/admin" className={`group flex items-center px-4 py-3 text-slate-600 font-medium no-underline rounded-lg transition-all duration-200 hover:bg-slate-50 hover:text-teal-600 hover:shadow-modern-xs ${isActive('/admin') ? 'bg-teal-50 text-teal-600 shadow-modern-xs border border-teal-100' : ''}`}>
            <i className="fas fa-robot mr-4 w-5 text-center text-lg group-hover:scale-110 transition-transform duration-200"></i>
            <span className="text-sm">Configuración IA</span>
          </Link>
        )}
        {isAdministrador && (
          <Link to="/audit" className={`group flex items-center px-4 py-3 text-slate-600 font-medium no-underline rounded-lg transition-all duration-200 hover:bg-slate-50 hover:text-teal-600 hover:shadow-modern-xs ${isActive('/audit') ? 'bg-teal-50 text-teal-600 shadow-modern-xs border border-teal-100' : ''}`}>
            <i className="fas fa-user-secret mr-4 w-5 text-center text-lg group-hover:scale-110 transition-transform duration-200"></i>
            <span className="text-sm">Auditoría de Usuario</span>
          </Link>
        )}
        {isAdministrador && (
          <Link to="/audit-logs" className={`group flex items-center px-4 py-3 text-slate-600 font-medium no-underline rounded-lg transition-all duration-200 hover:bg-slate-50 hover:text-teal-600 hover:shadow-modern-xs ${isActive('/audit-logs') ? 'bg-teal-50 text-teal-600 shadow-modern-xs border border-teal-100' : ''}`}>
            <i className="fas fa-history mr-4 w-5 text-center text-lg group-hover:scale-110 transition-transform duration-200"></i>
            <span className="text-sm">Logs de Auditoría</span>
          </Link>
        )}
      </nav>
      <div className="p-6 border-t border-slate-100">
        <button onClick={handleLogout} className="w-full group flex items-center px-4 py-3 text-slate-600 font-medium no-underline rounded-lg transition-all duration-200 hover:bg-red-50 hover:text-red-600 hover:shadow-modern-xs">
          <i className="fas fa-sign-out-alt mr-4 w-5 text-center text-lg group-hover:scale-110 transition-transform duration-200"></i>
          <span className="text-sm">Cerrar Sesión</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;