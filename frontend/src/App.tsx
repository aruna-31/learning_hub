import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import LandingPage from './pages/LandingPage';
import DashboardLayout from './layouts/DashboardLayout';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Lazy Loaded Pages
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const SearchPage = lazy(() => import('./pages/SearchPage'));
const RoadmapPage = lazy(() => import('./pages/RoadmapPage'));
const RoadmapsList = lazy(() => import('./pages/RoadmapsList'));
const BookmarksPage = lazy(() => import('./pages/BookmarksPage'));
const NotesPage = lazy(() => import('./pages/NotesPage'));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));

// Instantiate TanStack Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Guard Route for authenticated pages
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return <div className="min-h-screen flex items-center justify-center text-slate-400">Loading auth...</div>;
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

// Guard Route for guest-only pages (login/register)
function GuestRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return <div className="min-h-screen flex items-center justify-center text-slate-400">Loading auth...</div>;
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <>{children}</>;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Suspense fallback={
            <div className="min-h-screen flex flex-col items-center justify-center bg-slate-950 text-slate-400 gap-3">
              <div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
              <p className="text-sm font-medium">Loading LearnHub...</p>
            </div>
          }>
            <Routes>
              {/* Main Landing Route */}
              <Route path="/" element={<LandingPage />} />
              
              {/* Authentication Routes (Guest Only) */}
              <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
              <Route path="/register" element={<GuestRoute><RegisterPage /></GuestRoute>} />
              
              {/* Protected Routes inside DashboardLayout shell */}
              <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/search" element={<SearchPage />} />
                <Route path="/roadmap" element={<RoadmapsList />} />
                <Route path="/roadmap/:topic" element={<RoadmapPage />} />
                <Route path="/bookmarks" element={<BookmarksPage />} />
                <Route path="/notes" element={<NotesPage />} />
                <Route path="/analytics" element={<AnalyticsPage />} />
                <Route path="/profile" element={<ProfilePage />} />
              </Route>
              
              {/* Catch-all 404 Route */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
        
        {/* Toast Notifications */}
        <Toaster 
          position="top-right" 
          toastOptions={{
            style: {
              background: '#1E293B',
              color: '#F8FAFC',
              border: '1px solid rgba(100, 116, 139, 0.2)',
            },
          }}
        />
      </AuthProvider>
    </QueryClientProvider>
  );
}
