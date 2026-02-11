import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-50">
      <Sidebar isOpen={sidebarOpen} />
      <main className="flex-1 flex flex-col overflow-y-auto">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute top-6 left-6 bg-white text-slate-600 border border-slate-200 rounded-lg p-3 cursor-pointer z-10 text-lg shadow-modern-sm hover:bg-slate-50 hover:text-teal-600 transition-all duration-200 hover:shadow-modern"
        >
          <i className={`fas ${sidebarOpen ? 'fa-chevron-left' : 'fa-chevron-right'} text-sm`}></i>
        </button>
        <div id="main-content-area" className="h-full flex flex-col">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;