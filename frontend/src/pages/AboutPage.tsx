import React from 'react';
import { Sprout, ShieldCheck, Cpu, AlertTriangle, Layers, BookOpen } from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { Card } from '../components/common/Card';
import { Link } from 'react-router-dom';
import { Button } from '../components/common/Button';
import { useTranslation } from '../i18n';

export const AboutPage: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
      <PageHeader
        title={t('about.pageTitle')}
        subtitle={t('about.pageSubtitle')}
        showBackButton
        backTo="/"
      />

      {/* Mission Section */}
      <section className="mb-10 bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-xs">
        <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center mb-4">
          <Sprout className="w-7 h-7" />
        </div>
        <h2 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight mb-3">
          {t('about.purposeTitle')}
        </h2>
        <p className="text-sm sm:text-base text-slate-600 leading-relaxed mb-4">
          Plant diseases account for up to 40% of global crop losses annually, jeopardizing food security and smallholder farmer livelihoods. Often, by the time symptoms become obvious to untrained eyes, fungal and bacterial infections have already spread across the field.
        </p>
        <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
          <strong>AgriSmart AI</strong> was conceived as a farmer-first decision support tool. By transforming smartphones into early-warning plant diagnostic devices, we help agricultural producers detect foliar diseases at the initial stages, apply targeted organic remedies, and reduce unnecessary blanket pesticide use.
        </p>
      </section>

      {/* Technical Foundations */}
      <section className="mb-10 grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="border-slate-200">
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center mb-3">
            <Cpu className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 mb-2">
            {t('about.model1Title')}
          </h3>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-3">
            {t('about.model1Desc')}
          </p>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-700">
            <ShieldCheck className="w-4 h-4" />
            <span>{t('about.model1Badge')}</span>
          </div>
        </Card>

        <Card className="border-slate-200">
          <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center mb-3">
            <Layers className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 mb-2">
            {t('about.recommendationTitle')}
          </h3>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-3">
            {t('about.recommendationDesc')}
          </p>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-700">
            <BookOpen className="w-4 h-4" />
            <span>{t('about.recommendationBadge')}</span>
          </div>
        </Card>
      </section>

      {/* Responsible AI Disclaimer */}
      <section className="mb-10 p-6 rounded-3xl bg-amber-50 border border-amber-200 text-amber-950">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-6 h-6 text-amber-600 shrink-0 mt-1" />
          <div>
            <h3 className="text-base font-bold mb-1">{t('about.disclaimerTitle')}</h3>
            <p className="text-xs sm:text-sm text-amber-900 leading-relaxed">
              {t('about.disclaimerDesc')}
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <div className="text-center">
        <Link to="/scan">
          <Button variant="primary" size="lg">
            {t('nav.scanLeaf')}
          </Button>
        </Link>
      </div>
    </div>
  );
};
