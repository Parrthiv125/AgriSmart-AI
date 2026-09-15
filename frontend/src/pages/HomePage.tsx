import React from 'react';
import { Link } from 'react-router-dom';
import {
  Camera,
  ShieldCheck,
  Zap,
  Sprout,
  ArrowRight,
  Sparkles,
  Clock,
  HeartHandshake
} from 'lucide-react';
import { Button } from '../components/common/Button';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from '../i18n';

export const HomePage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const { t, getCropName } = useTranslation();

  const features = [
    {
      icon: <Zap className="w-6 h-6 text-amber-500" />,
      title: t('home.feature1Title'),
      description: t('home.feature1Desc')
    },
    {
      icon: <ShieldCheck className="w-6 h-6 text-emerald-600" />,
      title: t('home.feature2Title'),
      description: t('home.feature2Desc')
    },
    {
      icon: <Sprout className="w-6 h-6 text-green-600" />,
      title: t('home.feature3Title'),
      description: t('home.feature3Desc')
    },
    {
      icon: <Clock className="w-6 h-6 text-blue-600" />,
      title: t('home.feature4Title'),
      description: t('home.feature4Desc')
    }
  ];

  const steps = [
    {
      step: '01',
      title: t('home.step1Title'),
      description: t('home.step1Desc')
    },
    {
      step: '02',
      title: t('home.step2Title'),
      description: t('home.step2Desc')
    },
    {
      step: '03',
      title: t('home.step3Title'),
      description: t('home.step3Desc')
    }
  ];

  const rawCrops = [
    'Tomato', 'Potato', 'Corn (Maize)', 'Apple', 'Grape', 'Pepper Bell', 'Rice', 'Wheat'
  ];

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-emerald-900 via-emerald-800 to-slate-900 text-white pt-12 sm:pt-20 pb-20 sm:pb-28 px-4 sm:px-6 lg:px-8">
        {/* Soft background glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-5xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/10 backdrop-blur-md text-emerald-200 text-xs sm:text-sm font-semibold border border-white/15 mb-6 animate-pulse-subtle">
            <Sparkles className="w-4 h-4 text-emerald-300" />
            <span>{t('home.heroBadge')}</span>
          </div>

          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.15] mb-6 text-white">
            {t('home.heroTitlePrefix')} <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 via-teal-200 to-amber-200">
              {t('home.heroTitleHighlight')}
            </span>
          </h1>

          <p className="text-base sm:text-xl text-emerald-100/90 max-w-2xl mx-auto leading-relaxed mb-8 sm:mb-10">
            {t('home.heroSubtitle')}
          </p>

          {/* Call To Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 max-w-md mx-auto">
            <Link to={isAuthenticated ? '/scan' : '/scan'} className="w-full sm:w-auto">
              <Button
                variant="primary"
                size="lg"
                icon={<Camera className="w-5 h-5" />}
                className="w-full bg-emerald-500 hover:bg-emerald-400 text-emerald-950 font-bold shadow-lg shadow-emerald-500/25 border-emerald-400"
              >
                {t('home.scanLeafCta')}
              </Button>
            </Link>

            <Link to="/help" className="w-full sm:w-auto">
              <Button
                variant="outline"
                size="lg"
                className="w-full bg-white/10 hover:bg-white/20 text-white border-white/20 backdrop-blur-xs"
              >
                {t('nav.howItWorks')}
              </Button>
            </Link>
          </div>

          {/* Quick trust metrics */}
          <div className="mt-12 pt-8 border-t border-white/10 grid grid-cols-2 sm:grid-cols-4 gap-4 text-left sm:text-center text-xs text-emerald-200">
            <div>
              <p className="text-xl sm:text-2xl font-extrabold text-white">28</p>
              <p className="text-emerald-300/80">{t('home.statClassesLabel')}</p>
            </div>
            <div>
              <p className="text-xl sm:text-2xl font-extrabold text-white">&lt; 2 Sec</p>
              <p className="text-emerald-300/80">{t('home.statLatencyLabel')}</p>
            </div>
            <div>
              <p className="text-xl sm:text-2xl font-extrabold text-white">98.2%</p>
              <p className="text-emerald-300/80">{t('home.statAccuracyLabel')}</p>
            </div>
            <div>
              <p className="text-xl sm:text-2xl font-extrabold text-white">{t('disease.tabOrganic').split(' ')[0]}</p>
              <p className="text-emerald-300/80">& {t('disease.tabChemical').split(' ')[0]}</p>
            </div>
          </div>
        </div>
      </section>

      {/* 3-Step Simple Process */}
      <section className="py-16 sm:py-24 bg-white px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-12 sm:mb-16">
            <span className="text-xs font-bold text-emerald-600 uppercase tracking-widest block mb-2">
              {t('home.stepsTitle')}
            </span>
            <h2 className="text-2xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              {t('home.stepsSubtitle')}
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map((item, idx) => (
              <div
                key={idx}
                className="relative p-6 sm:p-8 rounded-3xl bg-slate-50 border border-slate-200/80 hover:border-emerald-300 hover:shadow-md transition-all group"
              >
                <span className="text-4xl font-black text-emerald-600/20 group-hover:text-emerald-600/40 transition-colors block mb-4">
                  {item.step}
                </span>
                <h3 className="text-xl font-bold text-slate-900 mb-2">{item.title}</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Supported Crops */}
      <section className="py-14 bg-slate-50 border-y border-slate-200/80 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto text-center">
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-6">
            {t('home.cropsTitle')}
          </h3>
          <div className="flex flex-wrap items-center justify-center gap-2.5 sm:gap-3">
            {rawCrops.map((crop, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white border border-slate-200 text-slate-800 text-xs sm:text-sm font-semibold shadow-2xs"
              >
                <Sprout className="w-4 h-4 text-emerald-600" />
                {getCropName(crop)}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits / Features Grid */}
      <section className="py-16 sm:py-24 bg-white px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-12 sm:mb-16">
            <span className="text-xs font-bold text-emerald-600 uppercase tracking-widest block mb-2">
              {t('home.featuresTitle')}
            </span>
            <h2 className="text-2xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              {t('home.featuresSubtitle')}
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, idx) => (
              <div
                key={idx}
                className="p-6 rounded-2xl bg-white border border-slate-200/90 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="w-12 h-12 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-center mb-4">
                    {feature.icon}
                  </div>
                  <h3 className="text-base font-bold text-slate-900 mb-2">{feature.title}</h3>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust & Community Callout */}
      <section className="py-12 bg-emerald-50/60 border-t border-emerald-200/60 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shrink-0">
              <HeartHandshake className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-base font-bold text-emerald-950">{t('home.ctaBannerTitle')}</h4>
              <p className="text-xs sm:text-sm text-emerald-800">
                {t('home.ctaBannerSubtitle')}
              </p>
            </div>
          </div>
          <Link to="/scan">
            <Button variant="primary" size="md" icon={<ArrowRight className="w-4 h-4" />}>
              {t('home.ctaBannerBtn')}
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
};
