export { I18nProvider, useTranslation } from './I18nContext';
export { SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, STORAGE_KEY, isValidLanguage } from './config';
export type { SupportedLanguage, LanguageConfig, TranslationDictionary } from './types';
export { getLocalizedDisease, getAllLocalizedDiseases, getLocalizedCropName } from './diseaseLocales';
