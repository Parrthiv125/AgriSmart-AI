import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Camera,
  Activity,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Sprout,
  Plus
} from 'lucide-react';
import { dashboardService } from '../services/dashboard';
import { DashboardData } from '../types/dashboard';
import { StatCard } from '../components/dashboard/StatCard';
import { QuickScanCard } from '../components/dashboard/QuickScanCard';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { ConfidenceBadge } from '../components/common/ConfidenceBadge';
import { LoadingState } from '../components/common/LoadingState';
import { EmptyState } from '../components/common/EmptyState';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from '../i18n';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const { t, getDisease } = useTranslation();
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const dashboardData = await dashboardService.getDashboardData();
        setData(dashboardData);
      } catch (err) {
        console.error('Failed to load dashboard', err);
      } finally {
        setIsLoading(false);
      }
    };
    loadDashboard();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <LoadingState message={t('common.loading')} />
      </div>
    );
  }

  const metrics = data?.metrics || {
    totalScans: 0,
    healthyCropsCount: 0,
    diseasedCropsCount: 0,
    uncertainCount: 0,
    scansThisWeek: 0,
    healthyPercentage: 100
  };

  const recentScans = data?.recentScans || [];
  const latestPrediction = data?.latestPrediction;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10">
      {/* Welcome & Farm Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <span className="text-xs font-bold text-emerald-700 uppercase tracking-widest block mb-1">
            {t('dashboard.growerOverview')}
          </span>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            {t('dashboard.welcomeBack')}, {user?.name || t('nav.farmer')}
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            {user?.farmName || 'Family Homestead Farm'} • {user?.location || 'Registered Farm'}
          </p>
        </div>

        <Link to="/scan">
          <Button
            variant="primary"
            size="md"
            icon={<Camera className="w-4 h-4" />}
            className="shadow-sm font-bold"
          >
            {t('dashboard.newScanBtn')}
          </Button>
        </Link>
      </div>

      {/* Hero Quick Scan Launchpad */}
      <div className="mb-8">
        <QuickScanCard />
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8">
        <StatCard
          title={t('dashboard.statTotalScans')}
          value={metrics.totalScans}
          subtitle={`${metrics.scansThisWeek} ${t('dashboard.statScansThisWeek')}`}
          icon={<Activity className="w-5 h-5" />}
          accent="blue"
        />
        <StatCard
          title={t('dashboard.statHealthyCrops')}
          value={metrics.healthyCropsCount}
          subtitle={`${metrics.healthyPercentage}% ${t('dashboard.statOfAllScans')}`}
          icon={<CheckCircle2 className="w-5 h-5" />}
          accent="emerald"
        />
        <StatCard
          title={t('dashboard.statDiseasesIdentified')}
          value={metrics.diseasedCropsCount}
          subtitle={t('dashboard.statActiveAttention')}
          icon={<AlertTriangle className="w-5 h-5" />}
          accent="amber"
        />
        <StatCard
          title={t('common.crop')}
          value={data?.commonCrops.length || 1}
          subtitle={t('dashboard.statUncertainScans')}
          icon={<Sprout className="w-5 h-5" />}
          accent="purple"
        />
      </div>

      {/* Main Grid: Latest Scan Highlight & Recent Scans */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Latest Prediction Card */}
        <div className="lg:col-span-1">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base sm:text-lg font-bold text-slate-900">{t('dashboard.latestScanTitle')}</h2>
            {latestPrediction && (
              <Link
                to={`/result/${latestPrediction.predictionId}`}
                className="text-xs font-semibold text-emerald-700 hover:text-emerald-800"
              >
                {t('dashboard.viewReport')}
              </Link>
            )}
          </div>

          {latestPrediction ? (() => {
            const localized = getDisease(latestPrediction.disease.classId || latestPrediction.disease.name);
            return (
              <Card hoverable className="overflow-hidden p-0 border-emerald-200">
                <div className="relative aspect-16/10 bg-slate-900 overflow-hidden">
                  <img
                    src={latestPrediction.imageUrl}
                    alt={latestPrediction.disease.name}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-3 left-3">
                    <ConfidenceBadge
                      level={latestPrediction.confidenceLevel}
                      percentage={latestPrediction.confidence}
                      size="sm"
                    />
                  </div>
                </div>

                <div className="p-5">
                  <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
                    <span>{latestPrediction.crop}</span>
                    <span>•</span>
                    <span>{new Date(latestPrediction.createdAt).toLocaleDateString()}</span>
                  </div>

                  <h3 className="text-lg font-bold text-slate-900 mb-1">
                    {localized?.displayName || latestPrediction.disease.name}
                  </h3>
                  {latestPrediction.disease.scientificName && (
                    <p className="text-xs italic text-slate-400 font-serif mb-3">
                      {latestPrediction.disease.scientificName}
                    </p>
                  )}

                  <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed mb-4">
                    {latestPrediction.explanation}
                  </p>

                  <Link
                    to={`/result/${latestPrediction.predictionId}`}
                    className="inline-flex items-center justify-between w-full pt-3 border-t border-slate-100 text-xs font-bold text-emerald-700 hover:text-emerald-800"
                  >
                    <span>{t('dashboard.viewReport')}</span>
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </Card>
            );
          })() : (
            <EmptyState
              title={t('dashboard.noScansYet')}
              message={t('dashboard.noScansDesc')}
              actionLabel={t('dashboard.firstScanBtn')}
              onAction={() => {}}
            />
          )}
        </div>

        {/* Recent Scan History List */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base sm:text-lg font-bold text-slate-900">{t('dashboard.recentScansTitle')}</h2>
            <Link
              to="/history"
              className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 flex items-center gap-1"
            >
              <span>{t('dashboard.viewAllLink')}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {recentScans.length > 0 ? (
            <div className="space-y-3">
              {recentScans.map((scan) => {
                const localizedScan = getDisease(scan.classId || scan.diseaseName);
                return (
                  <Link
                    key={scan.id}
                    to={`/result/${scan.predictionId}`}
                    className="block group"
                  >
                    <Card
                      hoverable
                      padding="sm"
                      className="flex items-center justify-between gap-4 group-hover:border-emerald-300"
                    >
                      <div className="flex items-center gap-3.5 min-w-0">
                        <div className="w-14 h-14 rounded-xl bg-slate-900 overflow-hidden shrink-0 border border-slate-200">
                          <img
                            src={scan.imageUrl}
                            alt={scan.crop}
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center gap-2 mb-0.5">
                            <span className="text-xs font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-md">
                              {scan.crop}
                            </span>
                            <span className="text-[11px] text-slate-400">
                              {new Date(scan.createdAt).toLocaleDateString()}
                            </span>
                          </div>
                          <h4 className="text-sm font-bold text-slate-900 truncate group-hover:text-emerald-700 transition-colors">
                            {localizedScan?.displayName || scan.diseaseName}
                          </h4>
                        </div>
                      </div>

                      <div className="flex items-center gap-3 shrink-0">
                        <ConfidenceBadge
                          level={scan.confidenceLevel}
                          percentage={scan.confidence}
                          size="sm"
                          showLabel={false}
                        />
                        <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-emerald-600 group-hover:translate-x-1 transition-all" />
                      </div>
                    </Card>
                  </Link>
                );
              })}
            </div>
          ) : (
            <Card className="p-8 text-center">
              <EmptyState
                title={t('dashboard.noScansYet')}
                message={t('dashboard.noScansDesc')}
                actionLabel={t('dashboard.firstScanBtn')}
                actionIcon={<Plus className="w-4 h-4" />}
                onAction={() => {}}
              />
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
