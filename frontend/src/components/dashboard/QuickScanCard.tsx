import React from 'react';
import { Link } from 'react-router-dom';
import { Camera, Sparkles, ArrowRight } from 'lucide-react';
import { Button } from '../common/Button';
import { useTranslation } from '../../i18n';

export const QuickScanCard: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-800 via-emerald-700 to-teal-800 text-white p-6 sm:p-8 shadow-lg shadow-emerald-900/20">
      {/* Decorative background leaf accents */}
      <div className="absolute -right-12 -bottom-12 w-64 h-64 rounded-full bg-emerald-500/10 pointer-events-none blur-2xl" />
      <div className="absolute right-6 top-6 opacity-10 pointer-events-none">
        <Camera className="w-32 h-32" />
      </div>

      <div className="relative z-10 max-w-xl">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-600/60 backdrop-blur-xs text-emerald-100 text-xs font-bold border border-emerald-400/30 mb-4">
          <Sparkles className="w-3.5 h-3.5 text-emerald-300" />
          Model 2 Active • Field Adapted
        </div>

        <h2 className="text-2xl sm:text-3xl font-black tracking-tight mb-2 text-white">
          {t('dashboard.quickScanTitle')}
        </h2>
        <p className="text-emerald-100 text-sm sm:text-base leading-relaxed mb-6">
          {t('dashboard.quickScanSubtitle')}
        </p>

        <div className="flex flex-wrap items-center gap-3">
          <Link to="/scan">
            <Button
              variant="secondary"
              size="lg"
              icon={<Camera className="w-5 h-5 text-emerald-800" />}
              className="bg-white hover:bg-emerald-50 text-emerald-900 font-bold shadow-md"
            >
              {t('dashboard.quickScanBtn')}
            </Button>
          </Link>
          <Link
            to="/help"
            className="inline-flex items-center gap-1.5 px-4 py-3 rounded-xl text-sm font-semibold text-emerald-100 hover:text-white hover:bg-emerald-700/50 transition-colors"
          >
            <span>{t('nav.helpGuide')}</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
};
