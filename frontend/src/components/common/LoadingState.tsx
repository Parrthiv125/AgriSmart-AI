import React from 'react';
import { Loader2 } from 'lucide-react';

export interface LoadingStateProps {
  message?: string;
  subMessage?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading agricultural data...',
  subMessage,
  size = 'md'
}) => {
  const sizeMap = {
    sm: 'w-6 h-6',
    md: 'w-10 h-10',
    lg: 'w-14 h-14'
  };

  return (
    <div className="flex flex-col items-center justify-center p-8 sm:p-12 text-center">
      <div className="relative flex items-center justify-center mb-4">
        <div className="absolute w-12 h-12 bg-emerald-100 rounded-full animate-ping opacity-75" />
        <Loader2 className={`${sizeMap[size]} text-emerald-600 animate-spin relative z-10`} />
      </div>
      <p className="text-base sm:text-lg font-semibold text-slate-800">{message}</p>
      {subMessage && <p className="mt-1 text-sm text-slate-500 max-w-sm">{subMessage}</p>}
    </div>
  );
};
