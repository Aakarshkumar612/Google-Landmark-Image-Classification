import { PredictionResponse, VRAMResponse } from '../types';

const API_BASE_URL = 'https://llm-based-landmark-image-analyzer.onrender.com';

export const predictLandmark = async (imageFile: File): Promise<PredictionResponse> => {
  const formData = new FormData();
  formData.append('file', imageFile);

  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    body: formData,
    mode: 'cors',
  });

  if (!response.ok) {
    throw new Error(`Prediction failed: ${response.statusText}`);
  }

  return response.json();
};

export const getVRAMStats = async (): Promise<VRAMResponse> => {
  const response = await fetch(`${API_BASE_URL}/vram`, {
    method: 'GET',
    mode: 'cors',
  });

  if (!response.ok) {
    throw new Error(`VRAM fetch failed: ${response.statusText}`);
  }

  return response.json();
};
