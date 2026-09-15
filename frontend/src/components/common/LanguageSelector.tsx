import React, { useState, useRef, useEffect } from 'react';
import { Globe, ChevronDown, Check } from 'lucide-react';
import { useTranslation, SUPPORTED_LANGUAGES, SupportedLanguage } from '../../i18n';

interface LanguageSelectorProps {
  variant?: 'desktop' | 'mobile';
  className?: string;
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  variant = 'desktop',
  className = ''
}) => {
  const { language, setLanguage } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  const currentConfig =
    SUPPORTED_LANGUAGES.find((lang) => lang.code === language) || SUPPORTED_LANGUAGES[0];

  // Close on outside click
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleOutsideClick);
    }
    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
    };
  }, [isOpen]);

  // Keyboard accessibility
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setIsOpen(false);
      triggerRef.current?.focus();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (!isOpen) {
        setIsOpen(true);
      } else {
        const nextIndex =
          (SUPPORTED_LANGUAGES.findIndex((l) => l.code === language) + 1) %
          SUPPORTED_LANGUAGES.length;
        setLanguage(SUPPORTED_LANGUAGES[nextIndex].code);
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (!isOpen) {
        setIsOpen(true);
      } else {
        const prevIndex =
          (SUPPORTED_LANGUAGES.findIndex((l) => l.code === language) - 1 + SUPPORTED_LANGUAGES.length) %
          SUPPORTED_LANGUAGES.length;
        setLanguage(SUPPORTED_LANGUAGES[prevIndex].code);
      }
    }
  };

  const handleSelectLanguage = (code: SupportedLanguage) => {
    setLanguage(code);
    setIsOpen(false);
    triggerRef.current?.focus();
  };

  if (variant === 'mobile') {
    return (
      <div className={`pt-2 border-t border-slate-100 ${className}`}>
        <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 px-1 flex items-center gap-1.5">
          <Globe className="w-3.5 h-3.5 text-emerald-600" />
          <span>Language / ભાષા / भाषा</span>
        </label>
        <div className="grid grid-cols-3 gap-1.5" role="radiogroup" aria-label="Select Language">
          {SUPPORTED_LANGUAGES.map((lang) => {
            const isSelected = lang.code === language;
            return (
              <button
                key={lang.code}
                type="button"
                role="radio"
                aria-checked={isSelected}
                onClick={() => setLanguage(lang.code)}
                className={`py-2 px-2.5 rounded-xl text-xs font-bold transition-all text-center flex flex-col items-center justify-center gap-0.5 cursor-pointer ${
                  isSelected
                    ? 'bg-emerald-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                <span className="text-[11px] leading-tight">{lang.nativeLabel}</span>
                {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-white mt-0.5" />}
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className={`relative inline-block text-left ${className}`} ref={dropdownRef}>
      <button
        ref={triggerRef}
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label={`Select language, currently ${currentConfig.nativeLabel}`}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-50 hover:bg-slate-100 text-slate-700 hover:text-slate-900 border border-slate-200/80 transition-all focus:outline-none focus:ring-2 focus:ring-emerald-500/50 cursor-pointer shadow-2xs"
      >
        <Globe className="w-4 h-4 text-emerald-600" aria-hidden="true" />
        <span className="font-bold">{currentConfig.nativeLabel}</span>
        <ChevronDown
          className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${
            isOpen ? 'rotate-180 text-emerald-600' : ''
          }`}
          aria-hidden="true"
        />
      </button>

      {isOpen && (
        <div
          role="listbox"
          aria-label="Language options"
          className="absolute right-0 mt-1.5 w-40 rounded-2xl bg-white border border-slate-200 shadow-xl py-1.5 z-50 animate-fade-in focus:outline-none"
        >
          {SUPPORTED_LANGUAGES.map((lang) => {
            const isSelected = lang.code === language;
            return (
              <button
                key={lang.code}
                type="button"
                role="option"
                aria-selected={isSelected}
                onClick={() => handleSelectLanguage(lang.code)}
                className={`w-full px-3.5 py-2 text-left text-xs font-semibold flex items-center justify-between transition-colors cursor-pointer ${
                  isSelected
                    ? 'bg-emerald-50 text-emerald-800 font-bold'
                    : 'text-slate-700 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                <div>
                  <span className="block">{lang.nativeLabel}</span>
                  <span className="text-[10px] text-slate-400 font-normal">
                    {lang.label} ({lang.code})
                  </span>
                </div>
                {isSelected && (
                  <Check className="w-3.5 h-3.5 text-emerald-600 shrink-0" aria-hidden="true" />
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
