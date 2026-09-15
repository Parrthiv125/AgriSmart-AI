import React, { ReactNode } from 'react';
import { Sprout } from 'lucide-react';
import { Button } from './Button';

export interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  message: string;
  actionLabel?: string;
  onAction?: () => void;
  actionIcon?: ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  message,
  actionLabel,
  onAction,
  actionIcon
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 sm:p-14 text-center rounded-2xl border-2 border-dashed border-slate-200 bg-white/60">
      <div className="w-16 h-16 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4 shadow-2xs">
        {icon || <Sprout className="w-8 h-8" />}
      </div>
      <h3 className="text-lg sm:text-xl font-bold text-slate-900">{title}</h3>
      <p className="mt-1 text-sm sm:text-base text-slate-500 max-w-sm">{message}</p>
      {actionLabel && onAction && (
        <Button
          onClick={onAction}
          icon={actionIcon}
          className="mt-6 shadow-sm"
        >
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
