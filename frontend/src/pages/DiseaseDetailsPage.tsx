import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  Sprout,
  ShieldCheck,
  AlertTriangle,
  Camera,
  Layers,
  Search,
  CheckCircle2
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { TreatmentAccordion } from '../components/disease/TreatmentAccordion';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { diseaseService } from '../services/disease';
import { DiseaseInfo } from '../types/disease';
import { useTranslation } from '../i18n';

export const DiseaseDetailsPage: React.FC = () => {
  const { classId } = useParams<{ classId: string }>();
  const navigate = useNavigate();
  const { t, getDisease, getAllDiseases, getCropName } = useTranslation();

  const [disease, setDisease] = useState<DiseaseInfo | null>(null);
  const [allDiseases, setAllDiseases] = useState<DiseaseInfo[]>([]);
  const [selectedCropFilter, setSelectedCropFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        const all = await diseaseService.getAllDiseases();
        setAllDiseases(all);

        if (classId) {
          const detail = await diseaseService.getDiseaseById(classId);
          if (detail) {
            setDisease(detail);
          } else {
            setErrorMessage(`Could not find a disease record with ID: "${classId}".`);
          }
        } else if (all.length > 0) {
          setDisease(all[0]);
        }
      } catch (err: any) {
        setErrorMessage(err.message || t('common.error'));
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [classId, t]);

  if (isLoading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <LoadingState message={t('common.loading')} />
      </div>
    );
  }

  if (errorMessage || !disease) {
    return (
      <div className="max-w-xl mx-auto px-4 py-12">
        <ErrorState
          title={t('disease.notFoundTitle')}
          message={errorMessage || t('disease.notFoundMessage')}
          onRetry={() => navigate('/disease/tomato_early_blight')}
          retryLabel={t('disease.viewTomatoEarlyBlight')}
        />
      </div>
    );
  }

  // Overlay localized disease metadata
  const localizedDisease = getDisease(disease.classId) || disease;
  const localizedCatalog = getAllDiseases();

  const rawCropsList = Array.from(new Set(allDiseases.map((d) => d.crop)));

  const filteredCatalog = localizedCatalog.filter((d) => {
    const matchesCrop = selectedCropFilter === 'all' || d.crop.toLowerCase() === selectedCropFilter.toLowerCase() || allDiseases.find(orig => orig.classId === d.classId)?.crop.toLowerCase() === selectedCropFilter.toLowerCase();
    const matchesSearch =
      !searchQuery ||
      d.displayName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.crop.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCrop && matchesSearch;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10">
      <PageHeader
        title={localizedDisease.displayName}
        subtitle={`${localizedDisease.crop} • ${localizedDisease.scientificName || t('disease.guideSubtitle')}`}
        showBackButton
        backTo="/dashboard"
        action={
          <Link to="/scan">
            <Button variant="primary" size="sm" icon={<Camera className="w-4 h-4" />}>
              {t('disease.diagnoseLeafBtn')}
            </Button>
          </Link>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Main Content: Disease In-Depth */}
        <div className="lg:col-span-8 space-y-8">
          {/* Overview Card */}
          <Card className="p-6 sm:p-8">
            <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-emerald-50 text-emerald-800 text-xs font-bold border border-emerald-200">
                <Sprout className="w-4 h-4" />
                {t('disease.targetCropLabel')}: {localizedDisease.crop}
              </span>
              <span
                className={`text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider ${
                  localizedDisease.isHealthy
                    ? 'bg-emerald-100 text-emerald-800'
                    : localizedDisease.severity === 'severe'
                    ? 'bg-rose-100 text-rose-800'
                    : 'bg-amber-100 text-amber-800'
                }`}
              >
                {localizedDisease.isHealthy ? t('disease.healthyCondition') : `${localizedDisease.severity} ${t('disease.severityLabel')}`}
              </span>
            </div>

            <p className="text-sm sm:text-base text-slate-700 leading-relaxed mb-6">
              {localizedDisease.description}
            </p>

            {/* Symptoms & Causes Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-6 border-t border-slate-100">
              <div>
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  {t('disease.visualSymptomsTitle')}
                </h3>
                <ul className="space-y-2 text-xs sm:text-sm text-slate-600">
                  {localizedDisease.symptoms.map((symptom, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-2 shrink-0" />
                      <span>{symptom}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  {t('disease.causesTitle')}
                </h3>
                <ul className="space-y-2 text-xs sm:text-sm text-slate-600">
                  {localizedDisease.causes.map((cause, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-2 shrink-0" />
                      <span>{cause}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Preventative Measures */}
            <div className="mt-6 pt-6 border-t border-slate-100">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                {t('disease.preventionTitle')}
              </h3>
              <ul className="space-y-2 text-xs sm:text-sm text-slate-600">
                {localizedDisease.prevention.map((prev, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 mt-2 shrink-0" />
                    <span>{prev}</span>
                  </li>
                ))}
              </ul>
            </div>
          </Card>

          {/* Actionable Treatment Options */}
          <div>
            <h3 className="text-lg sm:text-xl font-black text-slate-900 mb-3 flex items-center gap-2">
              <Layers className="w-5 h-5 text-emerald-600" />
              {t('disease.treatmentsTitle')}
            </h3>
            <TreatmentAccordion treatment={localizedDisease.treatment} caution={localizedDisease.caution} />
          </div>
        </div>

        {/* Sidebar: 28 Classes Catalog Navigator */}
        <div className="lg:col-span-4 space-y-5">
          <Card className="p-5 border-slate-200">
            <div className="flex items-center justify-between gap-2 mb-3">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                {t('disease.sidebarTitle')}
              </h3>
              <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md">
                {filteredCatalog.length} {t('disease.sidebarCount')}
              </span>
            </div>

            {/* Search Input */}
            <div className="relative mb-3">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder={t('disease.searchPlaceholder')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            {/* Crop Filter Badges */}
            <div className="flex flex-wrap gap-1 mb-4 pb-3 border-b border-slate-100">
              <button
                onClick={() => setSelectedCropFilter('all')}
                className={`px-2 py-1 rounded-lg text-[11px] font-semibold transition-colors cursor-pointer ${
                  selectedCropFilter === 'all'
                    ? 'bg-emerald-700 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {t('disease.filterAll')}
              </button>
              {rawCropsList.map((c) => (
                <button
                  key={c}
                  onClick={() => setSelectedCropFilter(c)}
                  className={`px-2 py-1 rounded-lg text-[11px] font-semibold transition-colors cursor-pointer ${
                    selectedCropFilter === c
                      ? 'bg-emerald-700 text-white'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {getCropName(c)}
                </button>
              ))}
            </div>

            {/* Diseases List - Note: URL preserves exact classId */}
            <div className="space-y-1.5 max-h-[480px] overflow-y-auto pr-1">
              {filteredCatalog.map((d) => {
                const isSelected = d.classId === localizedDisease.classId;
                return (
                  <Link
                    key={d.classId}
                    to={`/disease/${d.classId}`}
                    className={`block p-2.5 rounded-xl text-xs transition-all ${
                      isSelected
                        ? 'bg-emerald-50 text-emerald-900 font-bold border border-emerald-300 shadow-2xs'
                        : 'text-slate-700 hover:bg-slate-50 hover:text-slate-900'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1">
                      <span className="truncate">{d.displayName}</span>
                      <span className="text-[10px] text-slate-400 shrink-0">{d.crop}</span>
                    </div>
                  </Link>
                );
              })}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
