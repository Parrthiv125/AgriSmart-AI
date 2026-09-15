import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  Camera,
  BookOpen,
  Share2,
  Calendar,
  Cpu,
  CheckCircle2
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { ConfidenceBadge } from '../components/common/ConfidenceBadge';
import { ConfidenceMeter } from '../components/prediction/ConfidenceMeter';
import { LowConfidenceAlert } from '../components/prediction/LowConfidenceAlert';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { predictionService } from '../services/prediction';
import { PredictionResult } from '../types/prediction';
import { useToast } from '../context/ToastContext';
import { useTranslation } from '../i18n';

export const ResultPage: React.FC = () => {
  const { predictionId } = useParams<{ predictionId: string }>();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { t, getDisease, getCropName } = useTranslation();

  const [result, setResult] = useState<PredictionResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchPrediction = async () => {
      if (!predictionId) {
        setErrorMessage(t('result.notFoundMessage'));
        setIsLoading(false);
        return;
      }

      try {
        const pred = await predictionService.getPredictionById(predictionId);
        if (!pred) {
          setErrorMessage(t('result.notFoundMessage'));
          return;
        }
        setResult(pred);
      } catch (err: any) {
        setErrorMessage(err.message || t('common.error'));
      } finally {
        setIsLoading(false);
      }
    };

    fetchPrediction();
  }, [predictionId, t]);

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: `AgriSmart Diagnosis: ${result?.crop} - ${result?.disease.name}`,
        text: `Diagnosis: ${result?.disease.name} (${Math.round((result?.confidence || 0) * 100)}% confidence).`,
        url: window.location.href
      }).catch(() => {});
    } else {
      navigator.clipboard.writeText(window.location.href);
      showToast(t('result.shareToast'), 'info');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <LoadingState message={t('common.loading')} />
      </div>
    );
  }

  if (errorMessage || !result) {
    return (
      <div className="max-w-xl mx-auto px-4 py-12">
        <ErrorState
          title={t('result.notFoundTitle')}
          message={errorMessage || t('result.notFoundMessage')}
          onRetry={() => navigate('/scan')}
          retryLabel={t('result.newScanBtn')}
        />
      </div>
    );
  }

  const isLowConfidence = result.confidenceLevel === 'low';
  const isHealthy = result.disease.isHealthy;

  // Localized disease mapping based on classId
  const localizedDisease = result.disease.classId ? getDisease(result.disease.classId) : null;
  const localizedName = localizedDisease
    ? (isLowConfidence
        ? `${t('common.uncertain')}: ${localizedDisease.displayName}`
        : localizedDisease.displayName)
    : result.disease.name;
  const localizedCrop = localizedDisease?.crop || getCropName(result.crop);

  // Localized action recommendations
  const localizedActions = localizedDisease
    ? isHealthy
      ? [localizedDisease.prevention[0] || 'Maintain consistent drip irrigation.', 'Inspect underside of foliage weekly.']
      : [
          ...(localizedDisease.treatment.cultural.slice(0, 2)),
          ...(localizedDisease.treatment.organic.slice(0, 1))
        ]
    : result.recommendation.actions;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10">
      <PageHeader
        title={t('result.pageTitle')}
        subtitle={`${t('result.analyzedOn')} ${new Date(result.createdAt).toLocaleString()} • ${result.modelName || t('result.modelBadge')}`}
        showBackButton
        backTo="/dashboard"
        action={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              icon={<Share2 className="w-4 h-4" />}
              onClick={handleShare}
            >
              {t('result.shareBtn')}
            </Button>
            <Link to="/scan">
              <Button
                variant="primary"
                size="sm"
                icon={<Camera className="w-4 h-4" />}
              >
                {t('result.scanAnotherBtn')}
              </Button>
            </Link>
          </div>
        }
      />

      {/* Low Confidence Alert Banner */}
      {isLowConfidence && (
        <div className="mb-8">
          <LowConfidenceAlert confidence={result.confidence} />
        </div>
      )}

      {/* Main Results Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-10">
        {/* Left: Scanned Leaf Image */}
        <div className="lg:col-span-5 space-y-4">
          <div className="relative rounded-3xl overflow-hidden bg-slate-900 border border-slate-200 shadow-md aspect-4/3 sm:aspect-square">
            <img
              src={result.imageUrl}
              alt="Scanned crop foliage"
              className="w-full h-full object-cover"
            />
            <div className="absolute top-3 left-3">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900/80 backdrop-blur-md text-white text-xs font-bold border border-white/20">
                <Calendar className="w-3.5 h-3.5 text-emerald-400" />
                {new Date(result.createdAt).toLocaleDateString()}
              </span>
            </div>
            <div className="absolute bottom-3 right-3">
              <ConfidenceBadge level={result.confidenceLevel} percentage={result.confidence} size="sm" />
            </div>
          </div>

          <ConfidenceMeter confidence={result.confidence} level={result.confidenceLevel} />
        </div>

        {/* Right: Diagnosis Details */}
        <div className="lg:col-span-7 space-y-6">
          <Card className="border-slate-200/90 shadow-sm p-6 sm:p-7">
            {/* Top Badges */}
            <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
              <span className="inline-flex items-center gap-1 text-xs font-bold px-3 py-1 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200">
                {t('result.cropLabel')}: {localizedCrop}
              </span>
              <span className="inline-flex items-center gap-1 text-xs font-medium text-slate-400">
                <Cpu className="w-3.5 h-3.5 text-slate-400" />
                {result.modelName || 'EfficientNet-B2'}
              </span>
            </div>

            {/* Disease Heading */}
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight mb-1">
              {localizedName}
            </h2>
            {(localizedDisease?.scientificName || result.disease.scientificName) && (
              <p className="text-sm italic text-slate-500 font-serif mb-4">
                {t('result.pathogenLabel')}: {localizedDisease?.scientificName || result.disease.scientificName}
              </p>
            )}

            {/* AI Explanation / Description */}
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 text-xs sm:text-sm text-slate-700 leading-relaxed mb-6">
              <strong className="font-bold text-slate-900 block mb-1">
                {t('result.observationSummaryTitle')}:
              </strong>
              {localizedDisease ? localizedDisease.description : result.explanation}
            </div>

            {/* Recommended Next Actions */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  {t('result.recommendedActionsTitle')}
                </h3>
                {isHealthy ? (
                  <span className="text-xs font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-md">
                    {t('result.routineCareBadge')}
                  </span>
                ) : (
                  <span className="text-xs font-bold text-amber-700 bg-amber-100 px-2 py-0.5 rounded-md">
                    {t('result.mitigationPlanBadge')}
                  </span>
                )}
              </div>

              <div className="space-y-2.5">
                {localizedActions.map((action, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 p-3.5 rounded-xl bg-emerald-50/50 border border-emerald-100 text-xs sm:text-sm text-slate-800"
                  >
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <span>{action}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex flex-col sm:flex-row items-center gap-3 pt-4 border-t border-slate-100">
              {result.disease.classId && (
                <Link
                  to={`/disease/${result.disease.classId}`}
                  className="w-full sm:w-auto flex-1"
                >
                  <Button
                    variant="primary"
                    size="md"
                    icon={<BookOpen className="w-4 h-4" />}
                    className="w-full font-bold"
                  >
                    {t('result.exploreGuideBtn')}
                  </Button>
                </Link>
              )}

              <Link to="/scan" className="w-full sm:w-auto">
                <Button
                  variant="outline"
                  size="md"
                  icon={<Camera className="w-4 h-4" />}
                  className="w-full"
                >
                  {t('result.scanAnotherBottomBtn')}
                </Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
