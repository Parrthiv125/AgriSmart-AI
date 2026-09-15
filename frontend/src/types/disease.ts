export type DiseaseSeverity = 'none' | 'mild' | 'moderate' | 'severe';

export interface TreatmentOptions {
  cultural: string[];
  organic: string[];
  chemical: string[];
}

export interface DiseaseInfo {
  id: string;
  classId: string;
  displayName: string;
  scientificName?: string;
  crop: string;
  isHealthy: boolean;
  severity: DiseaseSeverity;
  description: string;
  symptoms: string[];
  causes: string[];
  prevention: string[];
  treatment: TreatmentOptions;
  caution: string;
  imageUrl?: string;
}
