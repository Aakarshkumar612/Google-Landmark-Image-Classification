import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { AlertCircle } from 'lucide-react';
import { Header } from './components/Header';
import { UploadZone } from './components/UploadZone';
import { ScanningAnimation } from './components/ScanningAnimation';
import { ResultsCard } from './components/ResultsCard';
import { HardwareMonitor } from './components/HardwareMonitor';
import { predictLandmark } from './services/api';
import { PredictionResponse } from './types';
import { useLanguage } from './contexts/LanguageContext';

type AppState = 'idle' | 'analyzing' | 'results' | 'error';

function App() {
  const [state, setState] = useState<AppState>('idle');
  const [imagePreview, setImagePreview] = useState<string>('');
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const { t } = useLanguage();

  const handleFileSelect = async (file: File) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result as string);
    };
    reader.readAsDataURL(file);

    setState('analyzing');
    setErrorMessage('');

    try {
      const prediction = await predictLandmark(file);
      setResult(prediction);
      setState('results');
    } catch (error) {
      setState('error');
      setErrorMessage(
        error instanceof Error ? error.message : 'Failed to analyze image'
      );
    }
  };

  const handleReset = () => {
    setState('idle');
    setImagePreview('');
    setResult(null);
    setErrorMessage('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950 dark:to-gray-900 transition-colors duration-300">
      <Header />
      <HardwareMonitor />

      <main className="pt-24 pb-12 px-6">
        <div className="max-w-7xl mx-auto">
          <AnimatePresence mode="wait">
            {state === 'idle' && (
              <motion.div
                key="idle"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-center justify-center min-h-[calc(100vh-12rem)]"
              >
                <div className="w-full max-w-2xl">
                  <UploadZone onFileSelect={handleFileSelect} />
                </div>
              </motion.div>
            )}

            {state === 'analyzing' && (
              <motion.div
                key="analyzing"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-center justify-center min-h-[calc(100vh-12rem)]"
              >
                <ScanningAnimation imagePreview={imagePreview} />
              </motion.div>
            )}

            {state === 'results' && result && (
              <motion.div
                key="results"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-center justify-center min-h-[calc(100vh-12rem)]"
              >
                <ResultsCard
                  result={result}
                  imagePreview={imagePreview}
                  onReset={handleReset}
                />
              </motion.div>
            )}

            {state === 'error' && (
              <motion.div
                key="error"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="flex items-center justify-center min-h-[calc(100vh-12rem)]"
              >
                <div className="max-w-md w-full">
                  <div className="backdrop-blur-xl bg-white/80 dark:bg-gray-900/80 rounded-2xl border border-red-200 dark:border-red-800 shadow-2xl p-8">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-12 h-12 rounded-xl bg-red-500/10 flex items-center justify-center">
                        <AlertCircle className="w-6 h-6 text-red-500" />
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                          {t('error')}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {errorMessage}
                        </p>
                      </div>
                    </div>

                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={handleReset}
                      className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all"
                    >
                      Try Again
                    </motion.button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}

export default App;
