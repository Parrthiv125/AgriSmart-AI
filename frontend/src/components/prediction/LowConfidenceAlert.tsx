import React from 'react';
import { AlertTriangle, Camera, Sun, Focus, Layers } from 'lucide-react';
import { Button } from '../common/Button';
import { Link } from 'react-router-dom';
import { useTranslation } from '../../i18n';

interface LowConfidenceAlertProps {
  confidence: number;
}

export const LowConfidenceAlert: React.FC<LowConfidenceAlertProps> = ({ confidence }) => {
  const percent = Math.round(confidence * 100);
  const { t } = useTranslation();

  return (
    <div className="bg-amber-50 border-2 border-amber-300 rounded-3xl p-5 sm:p-7 shadow-xs">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-2xl bg-amber-100 text-amber-800 flex items-center justify-center shrink-0 shadow-2xs">
          <AlertTriangle className="w-6 h-6 text-amber-600" />
        </div>

        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <h3 className="text-lg font-bold text-amber-950">
              {t('common.uncertain')} ({percent}% {t('common.confidence')})
            </h3>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-200 text-amber-900 font-bold">
              {t('result.lowConfidenceNotice')}
            </span>
          </div>

          <p className="text-sm text-amber-900 leading-relaxed mb-4">
            {t('scan.analyzingNotice')}
          </p>

          <div className="bg-white/80 rounded-2xl p-4 border border-amber-200/80 mb-5">
            <h4 className="text-xs font-bold text-amber-950 uppercase tracking-wider mb-2.5">
              {t('help.bestPracticesTitle')}:
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-slate-700">
              <div className="flex items-center gap-2">
                <Sun className="w-4 h-4 text-amber-600 shrink-0" />
                <span>Natural bright daylight</span>
              </div>
              <div className="flex items-center gap-2">
                <Focus className="w-4 h-4 text-amber-600 shrink-0" />
                <span>Focus sharp on leaf spots</span>
              </div>
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-amber-600 shrink-0" />
                <span>Single leaf filling 70%+ of frame</span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link to="/scan">
              <Button
                variant="primary"
                size="md"
                icon={<Camera className="w-4 h-4" />}
                className="bg-amber-600 hover:bg-amber-700 text-white border-amber-700/30"
              >
                {t('result.scanAnotherBtn')}
              </Button>
            </Link>
            <Link to="/help">
              <Button variant="outline" size="md">
                {t('nav.helpGuide')}
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
