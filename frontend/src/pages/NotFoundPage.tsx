import React from 'react';
import { Link } from 'react-router-dom';
import { Sprout, LayoutDashboard, Camera } from 'lucide-react';
import { Button } from '../components/common/Button';
import { useTranslation } from '../i18n';

export const NotFoundPage: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="min-h-[75vh] flex items-center justify-center px-4 py-16 text-center">
      <div className="max-w-md mx-auto">
        <div className="w-16 h-16 rounded-3xl bg-emerald-100 text-emerald-800 flex items-center justify-center mx-auto mb-6 shadow-md shadow-emerald-600/10">
          <Sprout className="w-9 h-9" />
        </div>

        <span className="text-xs font-black text-emerald-600 tracking-widest uppercase mb-2 block">
          {t('notFound.errorCode')}
        </span>
        <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight mb-3">
          {t('notFound.title')}
        </h1>
        <p className="text-sm text-slate-500 mb-8 leading-relaxed">
          {t('notFound.description')}
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link to="/dashboard" className="w-full sm:w-auto">
            <Button
              variant="primary"
              size="md"
              icon={<LayoutDashboard className="w-4 h-4" />}
              className="w-full font-bold"
            >
              {t('notFound.dashboardBtn')}
            </Button>
          </Link>
          <Link to="/scan" className="w-full sm:w-auto">
            <Button
              variant="outline"
              size="md"
              icon={<Camera className="w-4 h-4" />}
              className="w-full"
            >
              {t('notFound.scanBtn')}
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};
