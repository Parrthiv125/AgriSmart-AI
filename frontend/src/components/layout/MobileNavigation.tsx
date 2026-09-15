import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Camera, History, BookOpen, HelpCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useTranslation } from '../../i18n';

export const MobileNavigation: React.FC = () => {
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  const { t } = useTranslation();

  const isActive = (path: string) => {
    if (path === '/dashboard' && location.pathname === '/') return false;
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-lg border-t border-slate-200 shadow-lg px-2 pb-[env(safe-area-inset-bottom,8px)] pt-1.5">
      <div className="flex items-center justify-around max-w-md mx-auto relative">
        {/* Dashboard */}
        <Link
          to={isAuthenticated ? '/dashboard' : '/'}
          className={`flex flex-col items-center justify-center min-w-[60px] py-1 text-[11px] font-semibold transition-colors ${
            isActive(isAuthenticated ? '/dashboard' : '/')
              ? 'text-emerald-600 font-bold'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <LayoutDashboard className="w-5 h-5 mb-0.5" />
          <span>{t('nav.home')}</span>
        </Link>

        {/* History */}
        <Link
          to="/history"
          className={`flex flex-col items-center justify-center min-w-[60px] py-1 text-[11px] font-semibold transition-colors ${
            isActive('/history')
              ? 'text-emerald-600 font-bold'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <History className="w-5 h-5 mb-0.5" />
          <span>{t('nav.scanHistory').split(' ')[0]}</span>
        </Link>

        {/* Floating Scan Button (Center Action) */}
        <div className="relative -top-5 flex flex-col items-center">
          <Link
            to="/scan"
            className="w-14 h-14 rounded-full bg-gradient-to-tr from-emerald-700 to-emerald-500 text-white flex items-center justify-center shadow-lg shadow-emerald-600/40 hover:scale-105 active:scale-95 transition-all border-4 border-white"
            aria-label={t('nav.scanLeaf')}
          >
            <Camera className="w-6 h-6" />
          </Link>
          <span className="text-[11px] font-bold text-emerald-700 mt-1">
            {t('nav.scanLeaf').split(' ')[0]}
          </span>
        </div>

        {/* Disease Catalog */}
        <Link
          to="/disease/tomato_early_blight"
          className={`flex flex-col items-center justify-center min-w-[60px] py-1 text-[11px] font-semibold transition-colors ${
            isActive('/disease')
              ? 'text-emerald-600 font-bold'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <BookOpen className="w-5 h-5 mb-0.5" />
          <span>{t('nav.diseaseGuide').split(' ')[0]}</span>
        </Link>

        {/* Help */}
        <Link
          to="/help"
          className={`flex flex-col items-center justify-center min-w-[60px] py-1 text-[11px] font-semibold transition-colors ${
            isActive('/help')
              ? 'text-emerald-600 font-bold'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <HelpCircle className="w-5 h-5 mb-0.5" />
          <span>{t('nav.helpGuide').split(' ')[0]}</span>
        </Link>
      </div>
    </nav>
  );
};
