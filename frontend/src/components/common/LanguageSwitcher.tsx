import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

interface Language {
  code: string;
  name: string;
  flag: string;
}

const languages: Language[] = [
  { code: 'es', name: 'Español', flag: '/es.jpg' },
  { code: 'en', name: 'English', flag: '/en.jpg' },
  { code: 'pt', name: 'Português', flag: '/pt.jpg' }
];

const LanguageSwitcher: React.FC = () => {
  const { i18n } = useTranslation();
  const [currentLanguage, setCurrentLanguage] = useState(i18n.language || 'es');

  const handleLanguageChange = (languageCode: string) => {
    setCurrentLanguage(languageCode);
    i18n.changeLanguage(languageCode);
  };

  return (
    <div className="language-switcher">
      {languages.map((lang) => (
        <img
          key={lang.code}
          src={lang.flag}
          alt={lang.name}
          className={`language-flag-img ${currentLanguage === lang.code ? 'active' : ''}`}
          onClick={() => handleLanguageChange(lang.code)}
          title={lang.name}
        />
      ))}
    </div>
  );
};

export default LanguageSwitcher;