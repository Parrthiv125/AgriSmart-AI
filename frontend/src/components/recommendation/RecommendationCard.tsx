import React from 'react';
import { ShieldCheck, CheckCircle2, Clock } from 'lucide-react';
import { RecommendationPlan } from '../../types/recommendation';
import { Card } from '../common/Card';

interface RecommendationCardProps {
  plan: RecommendationPlan;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ plan }) => {
  const urgencyStyles = {
    critical: 'bg-rose-50 text-rose-800 border-rose-200',
    high: 'bg-orange-50 text-orange-800 border-orange-200',
    moderate: 'bg-amber-50 text-amber-800 border-amber-200',
    low: 'bg-emerald-50 text-emerald-800 border-emerald-200'
  }[plan.urgencyLevel];

  return (
    <Card className="border-emerald-200/80 shadow-sm bg-gradient-to-b from-white to-emerald-50/20">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-4 border-b border-slate-100">
        <div>
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">
            Farmer Action Plan
          </span>
          <h3 className="text-xl font-bold text-slate-900">{plan.headline}</h3>
        </div>
        <span
          className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border uppercase tracking-wider ${urgencyStyles}`}
        >
          <Clock className="w-3.5 h-3.5" />
          {plan.urgencyLevel} Urgency
        </span>
      </div>

      <p className="text-sm text-slate-600 mb-6 leading-relaxed">{plan.summary}</p>

      {/* Action Items */}
      <div className="space-y-3 mb-6">
        {plan.actions.map((action) => (
          <div
            key={action.id}
            className={`p-4 rounded-2xl border transition-all ${
              action.isUrgent
                ? 'bg-rose-50/60 border-rose-200 text-rose-950'
                : 'bg-white border-slate-200 text-slate-800 shadow-2xs'
            }`}
          >
            <div className="flex items-start gap-3">
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5 font-bold text-xs ${
                  action.isUrgent
                    ? 'bg-rose-600 text-white'
                    : 'bg-emerald-100 text-emerald-800'
                }`}
              >
                {action.isUrgent ? '!' : <CheckCircle2 className="w-4 h-4" />}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-0.5">
                  <h4 className="text-sm font-bold">{action.title}</h4>
                  <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-md bg-slate-100 text-slate-600">
                    {action.category}
                  </span>
                </div>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  {action.description}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Field disclaimer */}
      <div className="flex items-start gap-2.5 p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-500">
        <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
        <span>{plan.disclaimer}</span>
      </div>
    </Card>
  );
};
