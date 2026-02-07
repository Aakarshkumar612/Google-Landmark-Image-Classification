import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Language } from '../types';

interface LanguageContextType {
  language: Language;
  toggleLanguage: () => void;
  t: (key: string) => string;
}

const translations = {
  en: {
    appTitle: 'Landmark.AI',
    appSubtitle: 'Hybrid Vision Intelligence',
    uploadTitle: 'Upload Landmark Image',
    uploadSubtitle: 'Drag & drop or click to select an image',
    uploadButton: 'Select Image',
    analyzing: 'Analyzing Image...',
    results: 'Analysis Results',
    landmarkName: 'Landmark',
    description: 'Description',
    systemStatus: 'System Status',
    vramUsage: 'VRAM Usage',
    processing: 'Processing with Hybrid AI Engine',
    error: 'Error',
  },
  hi: {
    appTitle: 'लैंडमार्क.AI',
    appSubtitle: 'हाइब्रिड विज़न इंटेलिजेंस',
    uploadTitle: 'लैंडमार्क छवि अपलोड करें',
    uploadSubtitle: 'ड्रैग और ड्रॉप करें या छवि चुनें',
    uploadButton: 'छवि चुनें',
    analyzing: 'छवि का विश्लेषण हो रहा है...',
    results: 'विश्लेषण परिणाम',
    landmarkName: 'स्थल',
    description: 'विवरण',
    systemStatus: 'सिस्टम स्थिति',
    vramUsage: 'VRAM उपयोग',
    processing: 'हाइब्रिड AI इंजन के साथ प्रोसेसिंग',
    error: 'त्रुटि',
  },
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  const [language, setLanguage] = useState<Language>('en');
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    const savedLanguage = localStorage.getItem('landmark-language') as Language | null;
    if (savedLanguage && (savedLanguage === 'en' || savedLanguage === 'hi')) {
      setLanguage(savedLanguage);
    }
    setIsInitialized(true);
  }, []);

  useEffect(() => {
    if (isInitialized) {
      localStorage.setItem('landmark-language', language);
    }
  }, [language, isInitialized]);

  const toggleLanguage = () => {
    setLanguage((prev) => (prev === 'en' ? 'hi' : 'en'));
  };

  const t = (key: string): string => {
    return translations[language][key as keyof typeof translations.en] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
};
