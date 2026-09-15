import React from 'react';
import { ConfidenceLevel } from '../../types/prediction';
import { ConfidenceBadge } from '../common/ConfidenceBadge';
import { useTranslation } from '../../i18n';

interface ConfidenceMeterProps {
  confidence: number;
  level: ConfidenceLevel;
}

export const ConfidenceMeter: React.FC<ConfidenceMeterProps> = ({ confidence, level }) => {
  const { t } = useTranslation();
  const percentage = Math.round(confidence * 100);

  const getMeterGradient = () => {
    if (level === 'high') return 'from-emerald-500 to-emerald-600';
    if (level === 'medium') return 'from-amber-400 to-amber-500';
    return 'from-rose-500 to-rose-600';
  };

  return (
    <div className="w-full bg-white rounded-2xl p-4 sm:p-5 border border-slate-200/80 shadow-2xs">
      <div className="flex items-center justify-between gap-2 mb-2.5">
        <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
          {t('common.confidence')}
        </span>
        <ConfidenceBadge level={level} percentage={confidence} size="sm" />
      </div>

      <div className="w-full bg-slate-100 rounded-full h-3.5 overflow-hidden p-0.5 border border-slate-200">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${getMeterGradient()} transition-all duration-700 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-400 mt-1.5 font-medium">
        <span>0% ({t('common.uncertain')})</span>
        <span>50% ({t('common.mediumConfidence').split(' ')[0]})</span>
        <span>100% ({t('common.highConfidence').split(' ')[0]})</span>
      </div>
    </div>
  );
};
