import React from 'react';
import { Link } from 'react-router-dom';
import { Sprout, ShieldCheck, Heart } from 'lucide-react';
import { useTranslation } from '../../i18n';

export const Footer: React.FC = () => {
  const { t } = useTranslation();

  return (
    <footer className="bg-slate-900 text-slate-400 py-12 px-4 sm:px-6 lg:px-8 border-t border-slate-800 mb-16 md:mb-0">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8 pb-8 border-b border-slate-800 text-sm">
          {/* Brand Info */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2 text-white">
              <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center text-white">
                <Sprout className="w-5 h-5" />
              </div>
              <span className="text-xl font-bold">{t('common.appName')}</span>
            </div>
            <p className="text-slate-400 max-w-sm text-xs sm:text-sm leading-relaxed">
              {t('footer.brandDesc')}
            </p>
            <div className="flex items-center gap-2 text-xs text-emerald-400 font-medium">
              <ShieldCheck className="w-4 h-4" />
              <span>{t('footer.systemBadge')}</span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-white font-semibold text-xs tracking-wider uppercase mb-3">
              {t('footer.navTitle')}
            </h4>
            <ul className="space-y-2 text-xs sm:text-sm">
              <li>
                <Link to="/dashboard" className="hover:text-emerald-400 transition-colors">
                  {t('nav.dashboard')}
                </Link>
              </li>
              <li>
                <Link to="/scan" className="hover:text-emerald-400 transition-colors">
                  {t('nav.scanLeaf')}
                </Link>
              </li>
              <li>
                <Link to="/history" className="hover:text-emerald-400 transition-colors">
                  {t('nav.scanHistory')}
                </Link>
              </li>
              <li>
                <Link to="/disease/tomato_early_blight" className="hover:text-emerald-400 transition-colors">
                  {t('nav.diseaseGuide')}
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources & Support */}
          <div>
            <h4 className="text-white font-semibold text-xs tracking-wider uppercase mb-3">
              {t('footer.resourcesTitle')}
            </h4>
            <ul className="space-y-2 text-xs sm:text-sm">
              <li>
                <Link to="/help" className="hover:text-emerald-400 transition-colors">
                  {t('nav.helpGuide')}
                </Link>
              </li>
              <li>
                <Link to="/about" className="hover:text-emerald-400 transition-colors">
                  {t('nav.about')}
                </Link>
              </li>
              <li>
                <span className="text-slate-500">{t('footer.backendStatus')}</span>
              </li>
              <li>
                <span className="text-slate-500">{t('footer.classesCount')}</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Disclaimer & Copyright */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <p>
            &copy; {new Date().getFullYear()} {t('footer.copyright')}
          </p>
          <div className="flex items-center gap-1">
            <span>Designed for farmers with</span>
            <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500" />
            <span>field simplicity</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
