import React from 'react';
import { Trash2, RefreshCw, Sparkles, CheckCircle2 } from 'lucide-react';
import { Button } from '../common/Button';
import { useTranslation } from '../../i18n';

interface ImagePreviewProps {
  imageFile: File;
  previewUrl: string;
  onRemove: () => void;
  onChange: () => void;
  onAnalyze: () => void;
  isAnalyzing: boolean;
}

export const ImagePreview: React.FC<ImagePreviewProps> = ({
  imageFile,
  previewUrl,
  onRemove,
  onChange,
  onAnalyze,
  isAnalyzing
}) => {
  const { t } = useTranslation();
  const sizeKb = (imageFile.size / 1024).toFixed(0);

  return (
    <div className="w-full max-w-xl mx-auto bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden animate-fade-in">
      {/* Image Preview Window */}
      <div className="relative aspect-4/3 sm:aspect-16/10 bg-slate-900 flex items-center justify-center overflow-hidden group">
        <img
          src={previewUrl}
          alt="Selected crop leaf for diagnosis"
          className="w-full h-full object-contain"
        />

        {/* Top Badges */}
        <div className="absolute top-4 left-4 z-10 flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900/80 backdrop-blur-md text-emerald-400 text-xs font-semibold border border-slate-700">
            <CheckCircle2 className="w-3.5 h-3.5" />
            {t('scan.leafPreviewSubtitle')}
          </span>
        </div>
      </div>

      {/* Details & Actions */}
      <div className="p-5 sm:p-6">
        <div className="flex items-center justify-between gap-4 mb-5 pb-4 border-b border-slate-100 text-xs sm:text-sm text-slate-500">
          <div className="truncate">
            <p className="font-semibold text-slate-800 truncate">{imageFile.name}</p>
            <p className="text-[11px] text-slate-400">{sizeKb} KB • {imageFile.type}</p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={onChange}
              className="p-2 rounded-xl text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 transition-colors flex items-center gap-1 text-xs font-semibold cursor-pointer"
              title={t('scan.clearImage')}
            >
              <RefreshCw className="w-4 h-4" />
              <span className="hidden sm:inline">{t('scan.clearImage')}</span>
            </button>
            <button
              onClick={onRemove}
              className="p-2 rounded-xl text-slate-600 hover:text-rose-600 hover:bg-rose-50 transition-colors flex items-center gap-1 text-xs font-semibold cursor-pointer"
              title={t('common.cancel')}
            >
              <Trash2 className="w-4 h-4" />
              <span className="hidden sm:inline">{t('common.cancel')}</span>
            </button>
          </div>
        </div>

        {/* Primary CTA */}
        <Button
          variant="primary"
          size="lg"
          onClick={onAnalyze}
          isLoading={isAnalyzing}
          icon={<Sparkles className="w-5 h-5 text-emerald-200" />}
          className="w-full text-base font-bold shadow-md shadow-emerald-700/20"
        >
          {isAnalyzing ? t('scan.analyzingBtn') : t('scan.analyzeBtn')}
        </Button>
      </div>
    </div>
  );
};
