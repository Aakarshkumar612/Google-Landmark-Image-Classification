import { motion } from 'framer-motion';
import { Cpu, Sparkles } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

interface ScanningAnimationProps {
  imagePreview: string;
}

export const ScanningAnimation = ({ imagePreview }: ScanningAnimationProps) => {
  const { t } = useLanguage();

  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0.8, opacity: 0 }}
      transition={{ duration: 0.4 }}
      className="w-full max-w-2xl mx-auto"
    >
      <div className="relative rounded-2xl overflow-hidden backdrop-blur-xl bg-white/80 dark:bg-gray-900/80 border border-gray-200 dark:border-gray-800 shadow-2xl">
        <div className="relative">
          <img
            src={imagePreview}
            alt="Analyzing"
            className="w-full h-auto max-h-96 object-cover"
          />

          <motion.div
            animate={{ y: ['0%', '100%'] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            className="absolute inset-0 bg-gradient-to-b from-transparent via-indigo-500/40 to-transparent"
            style={{ height: '100px' }}
          />

          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />

          <motion.div
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="absolute inset-0 border-2 border-indigo-500"
          />

          <div className="absolute top-0 left-0 right-0 p-4">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 px-4 py-2 rounded-lg backdrop-blur-md bg-black/40 border border-indigo-500/50 w-fit"
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              >
                <Cpu className="w-5 h-5 text-indigo-400" />
              </motion.div>
              <span className="text-white font-medium text-sm">
                {t('processing')}
              </span>
            </motion.div>
          </div>
        </div>

        <div className="p-6 space-y-4">
          <div className="flex items-center gap-3">
            <motion.div
              animate={{ rotate: [0, 360] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
              className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center"
            >
              <Sparkles className="w-5 h-5 text-white" />
            </motion.div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {t('analyzing')}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Hybrid CNN + Gemini 2.5 Pro Engine
              </p>
            </div>
          </div>

          <div className="space-y-2">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                initial={{ width: '0%' }}
                animate={{ width: '100%' }}
                transition={{
                  duration: 1.5,
                  delay: i * 0.3,
                  repeat: Infinity,
                  repeatDelay: 0.9,
                }}
                className="h-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full"
              />
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};
