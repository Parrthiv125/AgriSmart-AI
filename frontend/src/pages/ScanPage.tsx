import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, UploadCloud, AlertCircle, Sprout } from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { ImageUploader } from '../components/scan/ImageUploader';
import { CameraCapture } from '../components/scan/CameraCapture';
import { ImagePreview } from '../components/scan/ImagePreview';
import { ScanProgress } from '../components/scan/ScanProgress';
import { predictionService } from '../services/prediction';
import { useToast } from '../context/ToastContext';
import { useTranslation } from '../i18n';

export const ScanPage: React.FC = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { t, getCropName } = useTranslation();

  const [activeMode, setActiveMode] = useState<'upload' | 'camera'>('upload');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [selectedCropHint, setSelectedCropHint] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const cropHints = ['Tomato', 'Potato', 'Corn (Maize)', 'Apple', 'Grape', 'Pepper Bell', 'Rice', 'Wheat'];

  const handleImageSelected = (file: File) => {
    setErrorMessage(null);
    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    showToast(t('scan.imageSelectedToast'), 'success');
  };

  const handleClearImage = () => {
    if (previewUrl && previewUrl.startsWith('blob:')) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
    setErrorMessage(null);
  };

  const handleError = (msg: string) => {
    setErrorMessage(msg);
    showToast(msg, 'error');
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      handleError('Please select or capture a leaf photo first.');
      return;
    }

    setIsAnalyzing(true);
    setErrorMessage(null);

    try {
      const result = await predictionService.predict(selectedFile, selectedCropHint || undefined);
      showToast(t('scan.diagnosisCompleteToast'), 'success');
      navigate(`/result/${result.predictionId}`);
    } catch (err: any) {
      console.error('Scan prediction error', err);
      setIsAnalyzing(false);
      handleError(err.message || 'Analysis failed. Please try a different photo.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10">
      <PageHeader
        title={t('scan.pageTitle')}
        subtitle={t('scan.pageSubtitle')}
        showBackButton
        backTo="/dashboard"
      />

      {/* Error alert */}
      {errorMessage && (
        <div className="mb-6 p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs sm:text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <strong className="font-bold block">{t('scan.notice')}:</strong>
            <span>{errorMessage}</span>
          </div>
        </div>
      )}

      {/* Progress State during active analysis */}
      {isAnalyzing && previewUrl ? (
        <div className="py-6">
          <ScanProgress previewUrl={previewUrl} />
        </div>
      ) : selectedFile && previewUrl ? (
        /* Image Preview & Ready to Analyze */
        <div className="space-y-6">
          {/* Optional Crop Hint Selector */}
          <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-2xs max-w-xl mx-auto">
            <div className="flex items-center gap-2 mb-2.5">
              <Sprout className="w-4 h-4 text-emerald-600" />
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                {t('scan.cropVarietyLabel')}
              </label>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {cropHints.map((crop) => {
                const isSelected = selectedCropHint === crop;
                return (
                  <button
                    key={crop}
                    type="button"
                    onClick={() => setSelectedCropHint(isSelected ? '' : crop)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-emerald-700 text-white shadow-xs'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {getCropName(crop)}
                  </button>
                );
              })}
            </div>
          </div>

          <ImagePreview
            imageFile={selectedFile}
            previewUrl={previewUrl}
            onChange={handleClearImage}
            onRemove={handleClearImage}
            onAnalyze={handleAnalyze}
            isAnalyzing={isAnalyzing}
          />
        </div>
      ) : (
        /* Choice: Upload vs Live Camera */
        <div className="space-y-6">
          {/* Mode Switcher Tabs */}
          <div className="flex max-w-md mx-auto rounded-2xl bg-slate-200/70 p-1.5 gap-1.5 border border-slate-200">
            <button
              onClick={() => setActiveMode('upload')}
              className={`flex-1 py-2.5 px-4 rounded-xl text-xs sm:text-sm font-bold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                activeMode === 'upload'
                  ? 'bg-white text-emerald-800 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <UploadCloud className="w-4 h-4" />
              <span>{t('scan.tabUpload')}</span>
            </button>
            <button
              onClick={() => setActiveMode('camera')}
              className={`flex-1 py-2.5 px-4 rounded-xl text-xs sm:text-sm font-bold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                activeMode === 'camera'
                  ? 'bg-white text-emerald-800 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Camera className="w-4 h-4" />
              <span>{t('scan.tabCamera')}</span>
            </button>
          </div>

          {activeMode === 'upload' ? (
            <div className="max-w-xl mx-auto">
              <ImageUploader
                onImageSelected={handleImageSelected}
                onError={handleError}
              />
            </div>
          ) : (
            <div className="max-w-xl mx-auto">
              <CameraCapture
                onPhotoCaptured={handleImageSelected}
                onCancel={() => setActiveMode('upload')}
                onError={handleError}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};
