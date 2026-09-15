import React, { useState } from 'react';
import {
  Camera,
  CheckCircle2,
  XCircle,
  HelpCircle,
  ChevronDown,
  ShieldCheck
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { Card } from '../components/common/Card';
import { Link } from 'react-router-dom';
import { Button } from '../components/common/Button';
import { useTranslation } from '../i18n';

export const HelpPage: React.FC = () => {
  const { t } = useTranslation();
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  const toggleFaq = (index: number) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  const dosAndDonts = [
    {
      do: 'Hold the camera 15-20 cm away so the leaf fills most of the screen.',
      dont: 'Taking photos from several feet away with busy background soil or clutter.'
    },
    {
      do: 'Use bright, natural daylight without heavy shadows.',
      dont: 'Taking photos in the dark, under fluorescent lamps, or with direct sun glare.'
    },
    {
      do: 'Focus sharply on the leaf spots or discolored margins.',
      dont: 'Submitting blurry or motion-shaken images taken while walking.'
    },
    {
      do: 'Inspect both top and underside; photograph where symptoms are clearest.',
      dont: 'Photographing dried, crushed, or completely dead fallen leaves.'
    }
  ];

  const faqs = [
    {
      q: 'How does AgriSmart AI detect crop diseases?',
      a: 'AgriSmart AI utilizes Model 1, a specialized computer vision neural network architecture (EfficientNet-B2). It is trained on tens of thousands of verified leaf images across 28 distinct agricultural disease and healthy crop categories. It analyzes lesion shapes, concentric rings, chlorosis patterns, and fungal pustules.'
    },
    {
      q: 'What does the Confidence Percentage mean?',
      a: 'The confidence score indicates how closely your photo matches known disease patterns. Scores above 80% indicate strong pattern match. Scores between 60% and 80% indicate moderate probability. When confidence drops below 60%, the system flags the scan as uncertain so you avoid applying unnecessary chemicals.'
    },
    {
      q: 'What should I do if my scan result has Low Confidence?',
      a: 'Do not panic and do not immediately purchase pesticides. Low confidence usually happens if the photo was blurry, shadowed, or taken from too far away. Take a fresh photo in good daylight with the leaf centered. If uncertain diagnoses persist, consult your district agricultural extension officer.'
    },
    {
      q: 'Can I use AgriSmart AI when I have weak internet in the fields?',
      a: 'Yes! The mobile interface is lightweight. Photos can be snapped using your phone camera and stored in your device gallery, then analyzed as soon as mobile connectivity or farm Wi-Fi is available.'
    },
    {
      q: 'Is AgriSmart AI a replacement for local agricultural extension officers?',
      a: 'No. AgriSmart AI is an AI-assisted decision support system designed to alert you early and provide actionable options. Always consult local agronomic guidelines and extension services before applying regulated synthetic chemicals.'
    }
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
      <PageHeader
        title={t('help.pageTitle')}
        subtitle={t('help.pageSubtitle')}
        showBackButton
        backTo="/dashboard"
      />

      {/* Photography Visual Guide Section */}
      <section className="mb-12">
        <div className="flex items-center gap-2 mb-4">
          <Camera className="w-5 h-5 text-emerald-600" />
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900">
            {t('help.bestPracticesTitle')}
          </h2>
        </div>
        <p className="text-sm text-slate-600 mb-6">
          {t('help.bestPracticesSubtitle')}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {dosAndDonts.map((item, idx) => (
            <Card key={idx} className="p-4 sm:p-5 border-slate-200">
              <div className="space-y-3 text-xs sm:text-sm">
                <div className="flex items-start gap-2.5 text-emerald-900 bg-emerald-50/80 p-3 rounded-xl border border-emerald-200/60">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                  <div>
                    <strong className="font-bold block text-emerald-950">{t('help.doLabel')}:</strong>
                    <span>{item.do}</span>
                  </div>
                </div>

                <div className="flex items-start gap-2.5 text-rose-900 bg-rose-50/80 p-3 rounded-xl border border-rose-200/60">
                  <XCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
                  <div>
                    <strong className="font-bold block text-rose-950">{t('help.dontLabel')}:</strong>
                    <span>{item.dont}</span>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Understanding Confidence Scores */}
      <section className="mb-12 bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-xs">
        <div className="flex items-center gap-2 mb-4">
          <ShieldCheck className="w-5 h-5 text-emerald-600" />
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900">
            {t('common.confidence')}
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-700 block mb-1">
              {t('common.highConfidence')} (&gt; 80%)
            </span>
            <p className="text-xs text-emerald-900 leading-relaxed">
              Clear diagnostic pattern detected. Immediate action steps and recommended treatments are highly reliable.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200">
            <span className="text-xs font-bold uppercase tracking-wider text-amber-700 block mb-1">
              {t('common.mediumConfidence')} (60% - 80%)
            </span>
            <p className="text-xs text-amber-900 leading-relaxed">
              Symptoms match known pathogen, but mild symptoms or lighting may obscure details. Confirm with symptoms guide.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200">
            <span className="text-xs font-bold uppercase tracking-wider text-rose-700 block mb-1">
              {t('common.lowConfidence')} (&lt; 60%)
            </span>
            <p className="text-xs text-rose-900 leading-relaxed">
              Uncertain result. Do not spray chemicals. Retake photo in natural daylight with sharp focus.
            </p>
          </div>
        </div>
      </section>

      {/* Frequently Asked Questions */}
      <section className="mb-12">
        <div className="flex items-center gap-2 mb-4">
          <HelpCircle className="w-5 h-5 text-emerald-600" />
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900">
            {t('help.faqTitle')}
          </h2>
        </div>

        <div className="space-y-3">
          {faqs.map((faq, idx) => {
            const isOpen = openFaq === idx;
            return (
              <div
                key={idx}
                className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-2xs transition-all"
              >
                <button
                  onClick={() => toggleFaq(idx)}
                  className="w-full px-5 py-4 flex items-center justify-between text-left text-sm sm:text-base font-bold text-slate-900 hover:text-emerald-700 transition-colors"
                >
                  <span>{faq.q}</span>
                  <ChevronDown
                    className={`w-5 h-5 text-slate-400 transition-transform shrink-0 ${
                      isOpen ? 'rotate-180 text-emerald-600' : ''
                    }`}
                  />
                </button>
                {isOpen && (
                  <div className="px-5 pb-5 pt-1 text-xs sm:text-sm text-slate-600 leading-relaxed border-t border-slate-100">
                    {faq.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* Ready to scan prompt */}
      <div className="p-6 rounded-3xl bg-emerald-600 text-white flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
        <div>
          <h3 className="text-lg font-bold">{t('help.readyToDiagnose')}</h3>
          <p className="text-xs sm:text-sm text-emerald-100">
            {t('help.needFurtherAssistance')}
          </p>
        </div>
        <Link to="/scan">
          <Button
            variant="secondary"
            size="md"
            icon={<Camera className="w-4 h-4 text-emerald-800" />}
            className="bg-white hover:bg-emerald-50 text-emerald-900 font-bold"
          >
            {t('help.startDiagnosingBtn')}
          </Button>
        </Link>
      </div>
    </div>
  );
};
