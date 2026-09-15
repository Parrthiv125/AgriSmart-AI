import { DiseaseService } from './DiseaseService';
import { DiseaseInfo } from '../../types/disease';
import { DISEASE_CATALOG, ALL_DISEASE_CLASSES } from '../../data/diseaseCatalog';

export class MockDiseaseService implements DiseaseService {
  async getAllDiseases(): Promise<DiseaseInfo[]> {
    await new Promise((res) => setTimeout(res, 100));
    return ALL_DISEASE_CLASSES;
  }

  async getDiseaseById(classId: string): Promise<DiseaseInfo | null> {
    await new Promise((res) => setTimeout(res, 120));
    return DISEASE_CATALOG[classId] || null;
  }

  async getDiseasesByCrop(crop: string): Promise<DiseaseInfo[]> {
    await new Promise((res) => setTimeout(res, 100));
    return ALL_DISEASE_CLASSES.filter(
      (d) => d.crop.toLowerCase() === crop.toLowerCase()
    );
  }

  async searchDiseases(query: string): Promise<DiseaseInfo[]> {
    await new Promise((res) => setTimeout(res, 150));
    const q = query.toLowerCase();
    return ALL_DISEASE_CLASSES.filter(
      (d) =>
        d.displayName.toLowerCase().includes(q) ||
        d.crop.toLowerCase().includes(q) ||
        d.symptoms.some((s) => s.toLowerCase().includes(q))
    );
  }
}
