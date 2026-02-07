import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, FileText, RefreshCw } from 'lucide-react';
import { PredictionResponse } from '../types';
import { useLanguage } from '../contexts/LanguageContext';

interface ResultsCardProps {
  result: PredictionResponse;
  imagePreview: string;
  onReset: () => void;
}

export const ResultsCard = ({ result, imagePreview, onReset }: ResultsCardProps) => {
  const { language, t } = useLanguage();

  const containerVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.5,
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      exit={{ opacity: 0, scale: 0.8 }}
      className="w-full max-w-4xl mx-auto"
    >
      <div className="rounded-2xl overflow-hidden backdrop-blur-xl bg-white/80 dark:bg-gray-900/80 border border-gray-200 dark:border-gray-800 shadow-2xl">
        <div className="relative">
          <img
            src={imagePreview}
            alt={result.name}
            className="w-full h-64 object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />

          <motion.div
            variants={itemVariants}
            className="absolute bottom-4 left-4 right-4"
          >
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-3xl font-bold text-white mb-2">{result.name}</h2>
                <div className="flex items-center gap-2 text-white/80">
                  <MapPin className="w-4 h-4" />
                  <span className="text-sm">{t('landmarkName')}</span>
                </div>
              </div>

              <motion.button
                whileHover={{ scale: 1.1, rotate: 180 }}
                whileTap={{ scale: 0.9 }}
                onClick={onReset}
                className="p-3 rounded-xl backdrop-blur-md bg-white/20 hover:bg-white/30 transition-colors"
                aria-label="Analyze another image"
              >
                <RefreshCw className="w-5 h-5 text-white" />
              </motion.button>
            </div>
          </motion.div>
        </div>

        <div className="p-8">
          <motion.div variants={itemVariants} className="mb-6">
            <div className="flex items-center gap-2 mb-4">
              <FileText className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                {t('description')}
              </h3>
            </div>
          </motion.div>

          <AnimatePresence mode="wait">
            <motion.div
              key={language}
              variants={itemVariants}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="p-6 rounded-xl backdrop-blur-sm bg-indigo-50 dark:bg-indigo-900/20 ring-2 ring-indigo-500"
            >
              <div className="flex items-center gap-2 mb-4">
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                    language === 'en'
                      ? 'bg-gradient-to-br from-blue-500 to-indigo-600'
                      : 'bg-gradient-to-br from-purple-500 to-pink-600'
                  }`}
                >
                  <span className="text-white font-bold text-sm">
                    {language === 'en' ? 'EN' : 'HI'}
                  </span>
                </div>
                <h4 className="font-semibold text-gray-900 dark:text-white">
                  {language === 'en' ? 'English' : 'हिन्दी'}
                </h4>
              </div>
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-lg">
                {language === 'en' ? result.english : result.hindi}
              </p>
            </motion.div>
          </AnimatePresence>

          <motion.div
            variants={itemVariants}
            className="mt-6 p-4 rounded-xl bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border border-indigo-500/20"
          >
            <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
              Powered by Hybrid CNN + Gemini 2.5 Pro
            </p>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
};
