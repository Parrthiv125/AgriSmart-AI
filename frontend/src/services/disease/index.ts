import { DiseaseService } from './DiseaseService';
import { MockDiseaseService } from './MockDiseaseService';
import { ApiDiseaseService } from './ApiDiseaseService';

const useMock = import.meta.env.VITE_USE_MOCK_API !== 'false';

export const diseaseService: DiseaseService = useMock
  ? new MockDiseaseService()
  : new ApiDiseaseService();

export * from './DiseaseService';
