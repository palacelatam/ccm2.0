import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import es from './es.json';
import en from './en.json';
import pt from './pt.json';

const resources = {
  es: { translation: es },
  en: { translation: en },
  pt: { translation: pt }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'es', // default language
    fallbackLng: 'es',
    interpolation: {
      escapeValue: false // React already escapes by default
    }
  });

export default i18n;