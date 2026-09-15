import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  Search,
  Calendar,
  Camera,
  Trash2,
  ArrowRight
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { ConfidenceBadge } from '../components/common/ConfidenceBadge';
import { LoadingState } from '../components/common/LoadingState';
import { EmptyState } from '../components/common/EmptyState';
import { historyService } from '../services/history';
import { HistoryItem, HistoryStatus } from '../types/history';
import { useToast } from '../context/ToastContext';
import { useTranslation } from '../i18n';

export const HistoryPage: React.FC = () => {
  const { predictionId } = useParams<{ predictionId?: string }>();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { t, getDisease } = useTranslation();

  const [items, setItems] = useState<HistoryItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<HistoryStatus | 'all'>('all');
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'confidence'>('newest');
  const [isLoading, setIsLoading] = useState(true);

  // If navigated to /history/:predictionId, auto-redirect or view
  useEffect(() => {
    if (predictionId) {
      navigate(`/result/${predictionId}`, { replace: true });
    }
  }, [predictionId, navigate]);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const historyList = await historyService.getHistory({
        searchQuery,
        status: selectedStatus,
        sortBy
      });
      setItems(historyList);
    } catch (err) {
      console.error('Failed to load history', err);
      showToast('Error loading history records', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [searchQuery, selectedStatus, sortBy]);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();

    if (window.confirm('Delete this diagnosis record from history?')) {
      const success = await historyService.deleteHistoryItem(id);
      if (success) {
        showToast(t('history.deleteItemToast'), 'info');
        loadHistory();
      }
    }
  };

  const statusFilters = [
    { id: 'all', label: t('history.filterStatusAll') },
    { id: 'diseased', label: t('history.filterDiseased') },
    { id: 'healthy', label: t('history.filterHealthy') },
    { id: 'uncertain', label: t('history.filterUncertain') }
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10">
      <PageHeader
        title={t('history.pageTitle')}
        subtitle={t('history.pageSubtitle')}
        showBackButton
        backTo="/dashboard"
        action={
          <Link to="/scan">
            <Button variant="primary" size="sm" icon={<Camera className="w-4 h-4" />}>
              {t('nav.scanLeaf')}
            </Button>
          </Link>
        }
      />

      {/* Filters & Search Toolbar */}
      <div className="bg-white rounded-3xl p-4 sm:p-5 border border-slate-200 shadow-2xs mb-8 space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search bar */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder={t('history.searchPlaceholder')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          {/* Sort selector */}
          <div className="flex items-center gap-2 shrink-0">
            <span className="text-xs font-bold text-slate-500 uppercase">{t('common.actions')}:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="newest">{t('history.sortNewest')}</option>
              <option value="oldest">{t('history.sortOldest')}</option>
              <option value="confidence">{t('history.sortConfidence')}</option>
            </select>
          </div>
        </div>

        {/* Status Filter Chips */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 pt-1 border-t border-slate-100">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mr-1 shrink-0">
            {t('disease.filterAll')}:
          </span>
          {statusFilters.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedStatus(tab.id as any)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-colors cursor-pointer ${
                selectedStatus === tab.id
                  ? 'bg-emerald-700 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* History List */}
      {isLoading ? (
        <div className="py-16">
          <LoadingState message={t('common.loading')} />
        </div>
      ) : items.length > 0 ? (
        <div className="space-y-3">
          {items.map((item) => {
            const localized = getDisease(item.classId);
            return (
              <Link
                key={item.id}
                to={`/result/${item.predictionId}`}
                className="block group"
              >
                <Card
                  hoverable
                  className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 group-hover:border-emerald-300"
                >
                  {/* Left: Thumbnail & Details */}
                  <div className="flex items-start sm:items-center gap-4 min-w-0">
                    <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-slate-900 overflow-hidden shrink-0 border border-slate-200">
                      <img
                        src={item.imageUrl}
                        alt={item.diseaseName}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                      />
                    </div>

                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <span className="text-xs font-bold text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-md border border-emerald-200/60">
                          {item.crop}
                        </span>
                        <span className="text-xs text-slate-400 flex items-center gap-1">
                          <Calendar className="w-3.5 h-3.5" />
                          {new Date(item.createdAt).toLocaleDateString()}
                        </span>
                      </div>

                      <h3 className="text-base sm:text-lg font-bold text-slate-900 truncate group-hover:text-emerald-700 transition-colors">
                        {localized?.displayName || item.diseaseName}
                      </h3>

                      {item.notes && (
                        <p className="text-xs text-slate-500 truncate mt-0.5">
                          {item.notes}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Right: Confidence badge & actions */}
                  <div className="flex items-center justify-between sm:justify-end gap-3 pt-3 sm:pt-0 border-t sm:border-t-0 border-slate-100">
                    <ConfidenceBadge
                      level={item.confidenceLevel}
                      percentage={item.confidence}
                      size="sm"
                    />

                    <div className="flex items-center gap-1">
                      <button
                        onClick={(e) => handleDelete(e, item.id)}
                        className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer"
                        title={t('history.deleteRecordTitle')}
                        aria-label={t('history.deleteRecordTitle')}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                      <div className="p-2 rounded-xl text-slate-300 group-hover:text-emerald-600 transition-colors">
                        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                      </div>
                    </div>
                  </div>
                </Card>
              </Link>
            );
          })}
        </div>
      ) : (
        <EmptyState
          title={t('history.emptyTitle')}
          message={
            searchQuery || selectedStatus !== 'all'
              ? t('history.emptyDesc')
              : t('dashboard.noScansDesc')
          }
          actionLabel={t('history.startScanBtn')}
          actionIcon={<Camera className="w-4 h-4" />}
          onAction={() => navigate('/scan')}
        />
      )}
    </div>
  );
};
