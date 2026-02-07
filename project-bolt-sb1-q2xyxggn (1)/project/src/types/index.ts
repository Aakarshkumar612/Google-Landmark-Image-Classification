export interface PredictionResponse {
  name: string;
  english: string;
  hindi: string;
}

export interface VRAMResponse {
  used_mhz: number;
  total_mhz: number;
  usage_percent: number;
}

export type Language = 'en' | 'hi';
export type Theme = 'dark' | 'light';
