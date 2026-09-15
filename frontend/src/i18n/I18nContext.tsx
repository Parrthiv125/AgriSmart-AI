import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import { SupportedLanguage, TranslationDictionary } from './types';
import { DEFAULT_LANGUAGE, STORAGE_KEY, isValidLanguage } from './config';
import { en } from './locales/en';
import { gu } from './locales/gu';
import { hi } from './locales/hi';
import {
  getLocalizedDisease,
  getAllLocalizedDiseases,
  getLocalizedCropName
} from './diseaseLocales';
import { DiseaseInfo } from '../types/disease';

const DICTIONARIES: Record<SupportedLanguage, TranslationDictionary> = {
  en,
  gu,
  hi
};

interface I18nContextValue {
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => void;
  t: (path: string, fallbackOrParams?: string | Record<string, string | number>) => string;
  getDisease: (classIdOrDisease: string | DiseaseInfo | null | undefined) => DiseaseInfo | null;
  getAllDiseases: () => DiseaseInfo[];
  getCropName: (crop: string) => string;
}

const I18nContext = createContext<I18nContextValue | undefined>(undefined);

function getInitialLanguage(): SupportedLanguage {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (isValidLanguage(saved)) {
      return saved;
    }
  } catch {
    // In case localStorage is blocked or restricted
  }
  return DEFAULT_LANGUAGE;
}

export const I18nProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<SupportedLanguage>(getInitialLanguage);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, language);
      document.documentElement.lang = language;
    } catch {
      // Storage unavailable
    }
  }, [language]);

  const setLanguage = useCallback((newLang: SupportedLanguage) => {
    if (isValidLanguage(newLang)) {
      setLanguageState(newLang);
    }
  }, []);

  const t = useCallback(
    (path: string, fallbackOrParams?: string | Record<string, string | number>): string => {
      const activeDict = DICTIONARIES[language] || DICTIONARIES.en;
      const fallbackDict = DICTIONARIES.en;

      const keys = path.split('.');
      let current: any = activeDict;
      let fallbackCurrent: any = fallbackDict;

      for (const key of keys) {
        if (current && typeof current === 'object') {
          current = current[key];
        } else {
          current = undefined;
        }

        if (fallbackCurrent && typeof fallbackCurrent === 'object') {
          fallbackCurrent = fallbackCurrent[key];
        } else {
          fallbackCurrent = undefined;
        }
      }

      let result = typeof current === 'string' ? current : typeof fallbackCurrent === 'string' ? fallbackCurrent : '';

      if (!result) {
        if (typeof fallbackOrParams === 'string') {
          return fallbackOrParams;
        }
        return path;
      }

      // Parameter replacement if provided e.g. {count: 5} for {{count}}
      if (typeof fallbackOrParams === 'object' && fallbackOrParams !== null) {
        Object.entries(fallbackOrParams).forEach(([pKey, pVal]) => {
          result = result.replace(new RegExp(`{{${pKey}}}`, 'g'), String(pVal));
        });
      }

      return result;
    },
    [language]
  );

  const getDisease = useCallback(
    (classIdOrDisease: string | DiseaseInfo | null | undefined): DiseaseInfo | null => {
      return getLocalizedDisease(classIdOrDisease, language);
    },
    [language]
  );

  const getAllDiseases = useCallback((): DiseaseInfo[] => {
    return getAllLocalizedDiseases(language);
  }, [language]);

  const getCropName = useCallback(
    (crop: string): string => {
      return getLocalizedCropName(crop, language);
    },
    [language]
  );

  const contextValue = useMemo(
    () => ({
      language,
      setLanguage,
      t,
      getDisease,
      getAllDiseases,
      getCropName
    }),
    [language, setLanguage, t, getDisease, getAllDiseases, getCropName]
  );

  return <I18nContext.Provider value={contextValue}>{children}</I18nContext.Provider>;
};

export function useTranslation() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useTranslation must be used within an I18nProvider');
  }
  return context;
}
