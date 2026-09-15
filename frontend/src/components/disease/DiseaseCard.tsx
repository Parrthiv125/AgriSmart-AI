import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ShieldAlert, CheckCircle2, Sprout } from 'lucide-react';
import { DiseaseInfo } from '../../types/disease';
import { Card } from '../common/Card';
import { useTranslation } from '../../i18n';

interface DiseaseCardProps {
  disease: DiseaseInfo;
}

export const DiseaseCard: React.FC<DiseaseCardProps> = ({ disease }) => {
  const { t, getDisease } = useTranslation();
  const localized = getDisease(disease.classId) || disease;

  const getSeverityBadge = () => {
    if (localized.isHealthy) {
      return (
        <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
          <CheckCircle2 className="w-3 h-3" /> {t('common.healthy')}
        </span>
      );
    }
    const colorMap: Record<string, string> = {
      none: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      mild: 'bg-blue-50 text-blue-800 border-blue-200',
      moderate: 'bg-amber-50 text-amber-800 border-amber-200',
      severe: 'bg-rose-50 text-rose-800 border-rose-200'
    };

    return (
      <span className={`inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${colorMap[localized.severity] || 'bg-slate-100 text-slate-800'} uppercase tracking-wider`}>
        <ShieldAlert className="w-3 h-3" /> {localized.severity} {t('disease.riskLabel')}
      </span>
    );
  };

  return (
    <Card hoverable className="flex flex-col justify-between h-full group">
      <div>
        <div className="flex items-start justify-between gap-2 mb-3">
          <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200/60">
            <Sprout className="w-3.5 h-3.5" />
            {localized.crop}
          </span>
          {getSeverityBadge()}
        </div>

        <h3 className="text-lg font-bold text-slate-900 group-hover:text-emerald-700 transition-colors">
          {localized.displayName}
        </h3>
        {localized.scientificName && (
          <p className="text-xs italic text-slate-400 mb-2 font-serif">
            {localized.scientificName}
          </p>
        )}

        <p className="text-xs sm:text-sm text-slate-600 line-clamp-2 leading-relaxed mb-4">
          {localized.description}
        </p>

        {/* Symptoms preview */}
        <div className="mb-4 pt-3 border-t border-slate-100">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            {t('disease.primarySymptoms')}
          </span>
          <p className="text-xs text-slate-600 truncate">
            {localized.symptoms[0] || 'Observe leaf patterns'}
          </p>
        </div>
      </div>

      <Link
        to={`/disease/${disease.classId}`}
        className="inline-flex items-center justify-between w-full pt-3 border-t border-slate-100 text-xs font-bold text-emerald-700 group-hover:text-emerald-800 transition-colors"
      >
        <span>{t('disease.viewGuideCard')}</span>
        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
      </Link>
    </Card>
  );
};
