import React from 'react';
import { ShieldCheck, AlertTriangle, HelpCircle } from 'lucide-react';
import { ConfidenceLevel } from '../../types/prediction';

export interface ConfidenceBadgeProps {
  level: ConfidenceLevel;
  percentage?: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({
  level,
  percentage,
  size = 'md',
  showLabel = true
}) => {
  const percentStr = percentage !== undefined ? `${Math.round(percentage * 100)}%` : '';

  const config = {
    high: {
      bg: 'bg-emerald-50 text-emerald-800 border-emerald-200/80',
      icon: <ShieldCheck className="shrink-0 text-emerald-600" />,
      label: 'High Confidence'
    },
    medium: {
      bg: 'bg-amber-50 text-amber-800 border-amber-200/80',
      icon: <AlertTriangle className="shrink-0 text-amber-600" />,
      label: 'Moderate Confidence'
    },
    low: {
      bg: 'bg-rose-50 text-rose-800 border-rose-200/80',
      icon: <HelpCircle className="shrink-0 text-rose-600" />,
      label: 'Low Confidence / Uncertain'
    }
  }[level];

  const sizeStyles = {
    sm: 'text-xs px-2.5 py-1 gap-1.5 [&_svg]:w-3.5 [&_svg]:h-3.5 font-medium',
    md: 'text-sm px-3 py-1.5 gap-2 [&_svg]:w-4 [&_svg]:h-4 font-semibold',
    lg: 'text-base px-4 py-2 gap-2.5 [&_svg]:w-5 [&_svg]:h-5 font-bold'
  }[size];

  return (
    <span
      className={`inline-flex items-center rounded-full border shadow-2xs ${config.bg} ${sizeStyles}`}
    >
      {config.icon}
      {percentStr && <span>{percentStr}</span>}
      {showLabel && <span>{config.label}</span>}
    </span>
  );
};
