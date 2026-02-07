import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Cpu, Activity } from 'lucide-react';
import { getVRAMStats } from '../services/api';
import { VRAMResponse } from '../types';
import { useLanguage } from '../contexts/LanguageContext';

export const HardwareMonitor = () => {
  const [vramData, setVramData] = useState<VRAMResponse | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [error, setError] = useState(false);
  const { t } = useLanguage();

  useEffect(() => {
    const fetchVRAM = async () => {
      try {
        const data = await getVRAMStats();
        setVramData(data);
        setError(false);
      } catch {
        setError(true);
      }
    };

    fetchVRAM();
    const interval = setInterval(fetchVRAM, 3000);

    return () => clearInterval(interval);
  }, []);

  if (error) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 100 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="fixed bottom-6 right-6 z-40"
    >
      <motion.div
        whileHover={{ scale: 1.02 }}
        onHoverStart={() => setIsExpanded(true)}
        onHoverEnd={() => setIsExpanded(false)}
        className="backdrop-blur-xl bg-white/80 dark:bg-gray-900/80 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-2xl overflow-hidden"
      >
        <div className="p-4">
          <div className="flex items-center gap-3">
            <motion.div
              animate={{ rotate: vramData ? 360 : 0 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center"
            >
              <Cpu className="w-5 h-5 text-white" />
            </motion.div>

            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h4 className="text-sm font-semibold text-gray-900 dark:text-white">
                  {t('systemStatus')}
                </h4>
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <Activity className="w-3 h-3 text-green-500" />
                </motion.div>
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                RTX 5050
              </p>
            </div>
          </div>

          <AnimatePresence>
            {isExpanded && vramData && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-800"
              >
                <div className="space-y-3">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-gray-600 dark:text-gray-400">
                        {t('vramUsage')}
                      </span>
                      <span className="text-xs font-semibold text-gray-900 dark:text-white">
                        {vramData.usage_percent.toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${vramData.usage_percent}%` }}
                        transition={{ duration: 0.5 }}
                        className="h-full bg-gradient-to-r from-green-500 to-emerald-600"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div className="p-2 rounded-lg bg-gray-50 dark:bg-gray-800">
                      <p className="text-xs text-gray-600 dark:text-gray-400">Used</p>
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">
                        {vramData.used_mhz.toFixed(0)} MB
                      </p>
                    </div>
                    <div className="p-2 rounded-lg bg-gray-50 dark:bg-gray-800">
                      <p className="text-xs text-gray-600 dark:text-gray-400">Total</p>
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">
                        {vramData.total_mhz.toFixed(0)} MB
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </motion.div>
  );
};
