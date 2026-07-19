import { useState } from 'react';
import { NavLink, useNavigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LayoutDashboard, Search, Map, Bookmark, FileText, BarChart3, 
  LogOut, Menu, X, ChevronRight 
} from 'lucide-react';

export default function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
    { name: 'Aggregated Search', path: '/search', icon: <Search className="w-5 h-5" /> },
    { name: 'Roadmaps', path: '/roadmap', icon: <Map className="w-5 h-5" /> },
    { name: 'Bookmarks', path: '/bookmarks', icon: <Bookmark className="w-5 h-5" /> },
    { name: 'Notes', path: '/notes', icon: <FileText className="w-5 h-5" /> },
    { name: 'Analytics', path: '/analytics', icon: <BarChart3 className="w-5 h-5" /> },
  ];

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen flex bg-[#0F172A]">
      
      {/* 1. Desktop Sidebar */}
      <aside className="hidden lg:flex flex-col w-64 bg-slate-900/60 border-r border-slate-800/80 backdrop-blur-xl shrink-0 p-6 justify-between">
        <div className="space-y-8">
          {/* Logo */}
          <div className="flex items-center gap-2" onClick={() => navigate('/dashboard')}>
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-bold text-white shadow-lg cursor-pointer">
              LH
            </div>
            <span className="text-lg font-bold tracking-tight text-white cursor-pointer select-none">
              LearnHub
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.name}
                to={item.path}
                className={({ isActive }) => `
                  flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all group
                  ${isActive 
                    ? 'bg-indigo-600/15 text-indigo-400 border-l-2 border-indigo-500' 
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
                  }
                `}
              >
                {item.icon}
                <span>{item.name}</span>
                <ChevronRight className="w-4 h-4 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Profile & Logout */}
        <div className="space-y-4 pt-6 border-t border-slate-800/80">
          {user && (
            <div 
              onClick={() => navigate('/profile')}
              className="flex items-center gap-3 px-2 cursor-pointer hover:bg-slate-800/40 p-1.5 rounded-xl transition-all"
            >
              <div className="w-10 h-10 rounded-xl overflow-hidden bg-slate-800 border border-slate-700/80 shrink-0">
                <img src={user.avatar || undefined} alt="User Avatar" className="w-full h-full object-cover" />
              </div>
              <div className="min-w-0">
                <h4 className="text-sm font-bold text-white truncate">{user.full_name}</h4>
                <p className="text-xs text-slate-500 truncate">{user.email}</p>
              </div>
            </div>
          )}

          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 text-sm font-medium text-slate-400 hover:text-rose-400 rounded-xl hover:bg-rose-500/10 transition-all"
          >
            <LogOut className="w-5 h-5" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* 2. Main Page Container */}
      <div className="flex-1 flex flex-col min-w-0">
        
        {/* Header Bar */}
        <header className="lg:hidden flex items-center justify-between px-6 py-4 bg-slate-900/40 border-b border-slate-800/80 backdrop-blur-xl">
          <div className="flex items-center gap-2" onClick={() => navigate('/dashboard')}>
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-bold text-white shadow-md">
              LH
            </div>
            <span className="text-base font-bold text-white">LearnHub</span>
          </div>

          <button
            onClick={() => setMobileOpen(true)}
            className="p-2 text-slate-400 hover:text-white rounded-lg bg-slate-800/50"
          >
            <Menu className="w-5 h-5" />
          </button>
        </header>

        {/* Dynamic Nested Content */}
        <main className="flex-1 overflow-y-auto px-6 py-8 lg:p-10 max-w-7xl mx-auto w-full">
          <Outlet />
        </main>
      </div>

      {/* 3. Mobile Navigation Drawer */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileOpen(false)}
              className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-xs z-40"
            />

            {/* Sidebar content */}
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="lg:hidden fixed top-0 bottom-0 left-0 w-64 bg-slate-950/95 border-r border-slate-800 z-50 p-6 flex flex-col justify-between"
            >
              <div className="space-y-8">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-bold text-white">
                      LH
                    </div>
                    <span className="text-base font-bold text-white">LearnHub</span>
                  </div>
                  <button
                    onClick={() => setMobileOpen(false)}
                    className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <nav className="space-y-1">
                  {navItems.map((item) => (
                    <NavLink
                      key={item.name}
                      to={item.path}
                      onClick={() => setMobileOpen(false)}
                      className={({ isActive }) => `
                        flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all
                        ${isActive 
                          ? 'bg-indigo-600/15 text-indigo-400 border-l-2 border-indigo-500' 
                          : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
                        }
                      `}
                    >
                      {item.icon}
                      <span>{item.name}</span>
                    </NavLink>
                  ))}
                </nav>
              </div>

              <div className="space-y-4 pt-6 border-t border-slate-800/80">
                {user && (
                  <div 
                    onClick={() => {
                      setMobileOpen(false);
                      navigate('/profile');
                    }}
                    className="flex items-center gap-3 px-2 cursor-pointer hover:bg-slate-800/40 p-1.5 rounded-xl transition-all"
                  >
                    <div className="w-9 h-9 rounded-lg overflow-hidden bg-slate-800 shrink-0">
                      <img src={user.avatar || undefined} alt="Avatar" className="w-full h-full object-cover" />
                    </div>
                    <div className="min-w-0">
                      <h4 className="text-xs font-bold text-white truncate">{user.full_name}</h4>
                      <p className="text-[10px] text-slate-500 truncate">{user.email}</p>
                    </div>
                  </div>
                )}
                <button
                  onClick={() => {
                    setMobileOpen(false);
                    handleLogout();
                  }}
                  className="w-full flex items-center gap-3 px-4 py-3 text-sm font-medium text-slate-400 hover:text-rose-400 rounded-xl hover:bg-rose-500/10 transition-all"
                >
                  <LogOut className="w-5 h-5" />
                  <span>Sign Out</span>
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

    </div>
  );
}
