import React, { ReactNode } from 'react';
import { Card } from '../common/Card';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: ReactNode;
  trend?: string;
  accent?: 'emerald' | 'amber' | 'blue' | 'purple';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  accent = 'emerald'
}) => {
  const accentStyles = {
    emerald: 'bg-emerald-50 text-emerald-700 border-emerald-200/60',
    amber: 'bg-amber-50 text-amber-700 border-amber-200/60',
    blue: 'bg-blue-50 text-blue-700 border-blue-200/60',
    purple: 'bg-purple-50 text-purple-700 border-purple-200/60'
  }[accent];

  return (
    <Card className="hover:border-slate-300 transition-colors">
      <div className="flex items-center justify-between gap-3 mb-3">
        <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
          {title}
        </span>
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center border shadow-2xs ${accentStyles}`}>
          {icon}
        </div>
      </div>

      <div className="flex items-baseline gap-2">
        <span className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          {value}
        </span>
        {trend && <span className="text-xs font-semibold text-emerald-600">{trend}</span>}
      </div>

      {subtitle && <p className="mt-1 text-xs text-slate-500">{subtitle}</p>}
    </Card>
  );
};
