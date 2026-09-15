import { apiClient } from './client';
import { DiseaseInfo } from '../../types/disease';

export const diseaseApi = {
  getAllDiseases: (): Promise<DiseaseInfo[]> => {
    return apiClient.get<DiseaseInfo[]>('/diseases');
  },

  getDiseaseByClassId: (classId: string): Promise<DiseaseInfo> => {
    return apiClient.get<DiseaseInfo>(`/diseases/${classId}`);
  },

  getDiseasesByCrop: (crop: string): Promise<DiseaseInfo[]> => {
    return apiClient.get<DiseaseInfo[]>('/diseases', { crop });
  }
};
