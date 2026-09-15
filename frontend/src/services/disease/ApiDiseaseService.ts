import { DiseaseService } from './DiseaseService';
import { DiseaseInfo } from '../../types/disease';
import { diseaseApi } from '../api/diseaseApi';

export class ApiDiseaseService implements DiseaseService {
  async getAllDiseases(): Promise<DiseaseInfo[]> {
    return diseaseApi.getAllDiseases();
  }

  async getDiseaseById(classId: string): Promise<DiseaseInfo | null> {
    try {
      return await diseaseApi.getDiseaseByClassId(classId);
    } catch {
      return null;
    }
  }

  async getDiseasesByCrop(crop: string): Promise<DiseaseInfo[]> {
    return diseaseApi.getDiseasesByCrop(crop);
  }

  async searchDiseases(query: string): Promise<DiseaseInfo[]> {
    const all = await this.getAllDiseases();
    const q = query.toLowerCase();
    return all.filter(
      (d) =>
        d.displayName.toLowerCase().includes(q) ||
        d.crop.toLowerCase().includes(q)
    );
  }
}
