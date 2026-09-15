import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Sprout, Camera, History, HelpCircle, Info, LayoutDashboard, LogOut, User as UserIcon, Menu, X } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../common/Button';
import { LanguageSelector } from '../common/LanguageSelector';
import { useTranslation } from '../../i18n';

export const Navbar: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navLinks = isAuthenticated
    ? [
        { name: t('nav.dashboard'), path: '/dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
        { name: t('nav.scanLeaf'), path: '/scan', icon: <Camera className="w-4 h-4" /> },
        { name: t('nav.scanHistory'), path: '/history', icon: <History className="w-4 h-4" /> },
        { name: t('nav.helpGuide'), path: '/help', icon: <HelpCircle className="w-4 h-4" /> },
        { name: t('nav.about'), path: '/about', icon: <Info className="w-4 h-4" /> }
      ]
    : [
        { name: t('nav.home'), path: '/', icon: <Sprout className="w-4 h-4" /> },
        { name: t('nav.howItWorks'), path: '/help', icon: <HelpCircle className="w-4 h-4" /> },
        { name: t('nav.aboutAgriSmart'), path: '/about', icon: <Info className="w-4 h-4" /> }
      ];

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActive = (path: string) => {
    if (path === '/' && location.pathname !== '/') return false;
    return location.pathname.startsWith(path);
  };

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">
          {/* Logo & Brand */}
          <Link
            to={isAuthenticated ? '/dashboard' : '/'}
            className="flex items-center gap-2.5 group focus:outline-none"
          >
            <div className="w-10 h-10 rounded-xl bg-emerald-600 flex items-center justify-center text-white shadow-md shadow-emerald-600/20 group-hover:bg-emerald-700 transition-colors">
              <Sprout className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight flex items-center gap-1">
                AgriSmart <span className="text-emerald-600">AI</span>
              </span>
              <span className="hidden sm:block text-[11px] font-medium text-slate-500 uppercase tracking-wider">
                {t('common.tagline')}
              </span>
            </div>
          </Link>

          {/* Desktop Nav Links */}
          <nav className="hidden md:flex items-center gap-1.5 lg:gap-2">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm font-semibold transition-all ${
                  isActive(link.path)
                    ? 'bg-emerald-50 text-emerald-700 font-bold border border-emerald-200/60 shadow-2xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
                }`}
              >
                {link.icon}
                <span>{link.name}</span>
              </Link>
            ))}
          </nav>

          {/* Desktop Right Side (Language + Auth / User) */}
          <div className="hidden md:flex items-center gap-2.5 lg:gap-3">
            <LanguageSelector variant="desktop" />

            {isAuthenticated ? (
              <div className="flex items-center gap-3 pl-3 border-l border-slate-200">
                <div className="flex items-center gap-2.5 text-left">
                  <div className="w-9 h-9 rounded-full bg-emerald-100 border border-emerald-300 text-emerald-800 flex items-center justify-center font-bold text-sm">
                    {user?.name ? user.name.charAt(0).toUpperCase() : <UserIcon className="w-4 h-4" />}
                  </div>
                  <div className="hidden lg:block">
                    <p className="text-xs font-bold text-slate-900 leading-tight truncate max-w-[130px]">
                      {user?.name || t('nav.farmer')}
                    </p>
                    <p className="text-[11px] text-slate-500 truncate max-w-[130px]">
                      {user?.farmName || 'Member'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-2 rounded-xl text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer"
                  title={t('nav.logout')}
                  aria-label={t('nav.logout')}
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link to="/login">
                  <Button variant="ghost" size="sm">
                    {t('nav.login')}
                  </Button>
                </Link>
                <Link to="/register">
                  <Button variant="primary" size="sm">
                    {t('nav.register')}
                  </Button>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Hamburger Button */}
          <div className="flex md:hidden items-center gap-2">
            {isAuthenticated && (
              <Link to="/scan">
                <Button size="sm" variant="primary" icon={<Camera className="w-4 h-4" />}>
                  {t('common.actions') === 'Actions' ? 'Scan' : t('nav.scanLeaf').split(' ')[0]}
                </Button>
              </Link>
            )}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2.5 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
              aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-3 pb-6 space-y-2 animate-fade-in shadow-xl">
          {isAuthenticated && user && (
            <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl mb-3 border border-slate-200">
              <div className="w-10 h-10 rounded-full bg-emerald-100 text-emerald-800 font-bold flex items-center justify-center text-base">
                {user.name.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-slate-900 truncate">{user.name}</p>
                <p className="text-xs text-slate-500 truncate">{user.farmName || user.email}</p>
              </div>
            </div>
          )}

          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              onClick={() => setIsMobileMenuOpen(false)}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl text-base font-semibold transition-colors ${
                isActive(link.path)
                  ? 'bg-emerald-50 text-emerald-700 font-bold border border-emerald-200'
                  : 'text-slate-700 hover:bg-slate-50'
              }`}
            >
              {link.icon}
              <span>{link.name}</span>
            </Link>
          ))}

          {/* Mobile Language Switcher inside hamburger menu */}
          <LanguageSelector variant="mobile" />

          <div className="pt-3 mt-3 border-t border-slate-100">
            {isAuthenticated ? (
              <Button
                variant="danger"
                size="md"
                onClick={() => {
                  setIsMobileMenuOpen(false);
                  handleLogout();
                }}
                icon={<LogOut className="w-4 h-4" />}
                className="w-full"
              >
                {t('nav.logout')}
              </Button>
            ) : (
              <div className="flex flex-col gap-2">
                <Link to="/login" onClick={() => setIsMobileMenuOpen(false)}>
                  <Button variant="outline" size="md" className="w-full">
                    {t('nav.login')}
                  </Button>
                </Link>
                <Link to="/register" onClick={() => setIsMobileMenuOpen(false)}>
                  <Button variant="primary" size="md" className="w-full">
                    {t('nav.register')}
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
