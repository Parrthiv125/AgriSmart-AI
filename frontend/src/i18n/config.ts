import { LanguageConfig, SupportedLanguage } from './types';

export const SUPPORTED_LANGUAGES: LanguageConfig[] = [
  {
    code: 'en',
    label: 'English',
    nativeLabel: 'English'
  },
  {
    code: 'gu',
    label: 'Gujarati',
    nativeLabel: 'ગુજરાતી'
  },
  {
    code: 'hi',
    label: 'Hindi',
    nativeLabel: 'हिन्दी'
  }
];

export const DEFAULT_LANGUAGE: SupportedLanguage = 'en';

export const STORAGE_KEY = 'agrismart_language';

export function isValidLanguage(code: unknown): code is SupportedLanguage {
  return typeof code === 'string' && ['en', 'gu', 'hi'].includes(code);
}
