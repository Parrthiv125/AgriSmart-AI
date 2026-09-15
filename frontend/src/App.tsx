import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { I18nProvider } from './i18n';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { Navbar } from './components/layout/Navbar';
import { MobileNavigation } from './components/layout/MobileNavigation';
import { Footer } from './components/layout/Footer';
import { ProtectedRoute } from './components/layout/ProtectedRoute';

// Public Pages
import { HomePage } from './pages/HomePage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { HelpPage } from './pages/HelpPage';
import { AboutPage } from './pages/AboutPage';

// Protected Pages
import { DashboardPage } from './pages/DashboardPage';
import { ScanPage } from './pages/ScanPage';
import { ResultPage } from './pages/ResultPage';
import { DiseaseDetailsPage } from './pages/DiseaseDetailsPage';
import { HistoryPage } from './pages/HistoryPage';

// Fallback Page
import { NotFoundPage } from './pages/NotFoundPage';

export function App() {
  return (
    <BrowserRouter>
      <I18nProvider>
        <AuthProvider>
          <ToastProvider>
            <div className="flex flex-col min-h-screen bg-slate-50 text-slate-900 selection:bg-emerald-100 selection:text-emerald-900">
              <Navbar />

            <main className="flex-1">
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/help" element={<HelpPage />} />
                <Route path="/about" element={<AboutPage />} />

                {/* Protected Routes */}
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <DashboardPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/scan"
                  element={
                    <ProtectedRoute>
                      <ScanPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/result/:predictionId"
                  element={
                    <ProtectedRoute>
                      <ResultPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/disease"
                  element={<Navigate to="/disease/tomato_early_blight" replace />}
                />
                <Route
                  path="/disease/:classId"
                  element={
                    <ProtectedRoute>
                      <DiseaseDetailsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/history"
                  element={
                    <ProtectedRoute>
                      <HistoryPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/history/:predictionId"
                  element={
                    <ProtectedRoute>
                      <HistoryPage />
                    </ProtectedRoute>
                  }
                />

                {/* 404 Catch-All Route */}
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </main>

            <Footer />
            <MobileNavigation />
          </div>
        </ToastProvider>
      </AuthProvider>
    </I18nProvider>
  </BrowserRouter>
  );
}

export default App;
