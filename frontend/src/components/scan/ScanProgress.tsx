import React, { useState, useEffect } from 'react';
import { Sparkles, Scan, CheckCircle2 } from 'lucide-react';
import { useTranslation } from '../../i18n';

interface ScanProgressProps {
  previewUrl: string;
}

export const ScanProgress: React.FC<ScanProgressProps> = ({ previewUrl }) => {
  const { t } = useTranslation();
  const [currentStageIdx, setCurrentStageIdx] = useState(0);
  const [progressPercent, setProgressPercent] = useState(15);

  const STAGES = [
    { label: t('scan.analyzingMessage'), duration: 500 },
    { label: t('scan.analyzingNotice'), duration: 600 },
    { label: 'EfficientNet-B2 Model 2 Inference...', duration: 700 },
    { label: t('result.recommendedActionsTitle'), duration: 400 }
  ];

  useEffect(() => {
    let accumulatedTime = 0;
    const timeouts: ReturnType<typeof setTimeout>[] = [];

    STAGES.forEach((stage, idx) => {
      accumulatedTime += stage.duration;
      const t = setTimeout(() => {
        setCurrentStageIdx(idx);
        setProgressPercent(Math.min(95, Math.round(((idx + 1) / STAGES.length) * 100)));
      }, accumulatedTime - stage.duration);
      timeouts.push(t);
    });

    return () => {
      timeouts.forEach(clearTimeout);
    };
  }, []);

  return (
    <div className="w-full max-w-md mx-auto p-6 sm:p-8 bg-white rounded-3xl border border-slate-200 shadow-xl text-center animate-fade-in">
      {/* Animated Image Viewport with Laser Scanner */}
      <div className="relative w-48 h-48 mx-auto rounded-2xl overflow-hidden bg-slate-900 border-2 border-emerald-500/40 shadow-inner mb-6">
        <img
          src={previewUrl}
          alt="Scanning leaf"
          className="w-full h-full object-cover filter contrast-110"
        />

        {/* Emerald Scanning Laser Line */}
        <div className="absolute left-0 right-0 h-1 bg-gradient-to-r from-emerald-400 via-emerald-200 to-emerald-400 shadow-[0_0_15px_#10b981] animate-scan-line pointer-events-none" />

        <div className="absolute inset-0 bg-emerald-950/20 backdrop-brightness-95 pointer-events-none" />

        {/* Center Scanner Overlay Icon */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-12 h-12 rounded-full bg-emerald-600/30 backdrop-blur-xs flex items-center justify-center text-emerald-300 animate-pulse">
            <Scan className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Headline */}
      <h3 className="text-xl sm:text-2xl font-black text-slate-900 mb-1 flex items-center justify-center gap-2">
        <Sparkles className="w-5 h-5 text-emerald-600" />
        {t('scan.analyzingBtn')}
      </h3>
      <p className="text-xs sm:text-sm text-slate-500 mb-6">
        {t('scan.analyzingNotice')}
      </p>

      {/* Progress Bar */}
      <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden mb-6 p-0.5 border border-slate-200">
        <div
          className="bg-gradient-to-r from-emerald-600 to-emerald-400 h-full rounded-full transition-all duration-500 ease-out"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Step Indicators */}
      <div className="space-y-2.5 text-left text-xs sm:text-sm">
        {STAGES.map((stage, idx) => {
          const isDone = idx < currentStageIdx;
          const isCurrent = idx === currentStageIdx;

          return (
            <div
              key={idx}
              className={`flex items-center gap-2.5 transition-colors ${
                isDone
                  ? 'text-emerald-700 font-medium'
                  : isCurrent
                  ? 'text-slate-900 font-bold'
                  : 'text-slate-400'
              }`}
            >
              {isDone ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              ) : isCurrent ? (
                <div className="w-4 h-4 rounded-full border-2 border-emerald-600 border-t-transparent animate-spin shrink-0" />
              ) : (
                <div className="w-4 h-4 rounded-full border border-slate-300 shrink-0" />
              )}
              <span className="truncate">{stage.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
