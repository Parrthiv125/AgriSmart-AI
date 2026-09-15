import { DiseaseInfo } from '../../types/disease';

export interface DiseaseService {
  getAllDiseases(): Promise<DiseaseInfo[]>;
  getDiseaseById(classId: string): Promise<DiseaseInfo | null>;
  getDiseasesByCrop(crop: string): Promise<DiseaseInfo[]>;
  searchDiseases(query: string): Promise<DiseaseInfo[]>;
}
