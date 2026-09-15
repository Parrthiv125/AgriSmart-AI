import React, { useState } from 'react';
import { Shovel, Leaf, FlaskConical, AlertTriangle } from 'lucide-react';
import { TreatmentOptions } from '../../types/disease';
import { useTranslation } from '../../i18n';

interface TreatmentAccordionProps {
  treatment: TreatmentOptions;
  caution: string;
}

export const TreatmentAccordion: React.FC<TreatmentAccordionProps> = ({ treatment, caution }) => {
  const [activeTab, setActiveTab] = useState<'cultural' | 'organic' | 'chemical'>('cultural');
  const { t } = useTranslation();

  const tabs = [
    {
      id: 'cultural' as const,
      label: t('disease.tabCultural'),
      icon: <Shovel className="w-4 h-4" />,
      items: treatment.cultural,
      accent: 'emerald',
      subtext: 'No-cost preventative field habits'
    },
    {
      id: 'organic' as const,
      label: t('disease.tabOrganic'),
      icon: <Leaf className="w-4 h-4" />,
      items: treatment.organic,
      accent: 'teal',
      subtext: 'Eco-friendly and certified bio-controls'
    },
    {
      id: 'chemical' as const,
      label: t('disease.tabChemical'),
      icon: <FlaskConical className="w-4 h-4" />,
      items: treatment.chemical,
      accent: 'blue',
      subtext: 'Targeted synthetic & protectant sprays'
    }
  ];

  return (
    <div className="w-full bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Tab Selector */}
      <div className="flex border-b border-slate-200 bg-slate-50/70 p-1.5 gap-1.5">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-3 px-2 sm:px-4 rounded-2xl flex flex-col sm:flex-row items-center justify-center gap-1.5 text-xs sm:text-sm font-bold transition-all cursor-pointer ${
                isActive
                  ? 'bg-white text-emerald-800 shadow-xs border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
              }`}
            >
              <div className="flex items-center gap-1.5">
                <span className={isActive ? 'text-emerald-600' : 'text-slate-400'}>{tab.icon}</span>
                <span>{tab.label}</span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="p-5 sm:p-7">
        {tabs.map((tab) => {
          if (activeTab !== tab.id) return null;
          return (
            <div key={tab.id} className="animate-fade-in space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                <p className="text-xs font-semibold text-slate-500">{tab.subtext}</p>
                <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                  {tab.items.length} {t('common.actions')}
                </span>
              </div>

              <ul className="space-y-3">
                {tab.items.map((item, idx) => (
                  <li
                    key={idx}
                    className="flex items-start gap-3 p-3.5 rounded-2xl bg-slate-50/70 border border-slate-100 text-xs sm:text-sm text-slate-800 leading-relaxed"
                  >
                    <span className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-800 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                      {idx + 1}
                    </span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}

        {/* Agricultural Extension Caution Disclaimer */}
        <div className="mt-6 pt-5 border-t border-slate-100 flex items-start gap-3 p-4 rounded-2xl bg-amber-50/80 border border-amber-200/80 text-xs sm:text-sm text-amber-950">
          <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <p>
            <strong className="font-bold">{t('disease.cautionLabel')}: </strong>
            {caution}
          </p>
        </div>
      </div>
    </div>
  );
};
