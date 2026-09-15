import { RecommendationService } from './RecommendationService';
import { RecommendationPlan, RecommendationAction } from '../../types/recommendation';
import { DISEASE_CATALOG } from '../../data/diseaseCatalog';

export class MockRecommendationService implements RecommendationService {
  async getRecommendationForDisease(classId: string): Promise<RecommendationPlan | null> {
    await new Promise((res) => setTimeout(res, 120));

    const disease = DISEASE_CATALOG[classId];
    if (!disease) return null;

    const actions: RecommendationAction[] = [];

    if (disease.isHealthy) {
      actions.push({
        id: 'act_healthy_1',
        category: 'cultural',
        title: 'Maintain Deep Soil Moisture',
        description: 'Provide regular drip irrigation to sustain vegetative vigor and root development.'
      });
      actions.push({
        id: 'act_healthy_2',
        category: 'cultural',
        title: 'Weekly Field Scouting',
        description: 'Inspect leaf undersides and new flush weekly for early indicators of seasonal pests or weather changes.'
      });
      return {
        classId,
        diseaseName: disease.displayName,
        crop: disease.crop,
        urgencyLevel: 'low',
        headline: `Foliage is Healthy and Vigorous`,
        summary: `Your ${disease.crop} crop displays no signs of disease. Continue standard good agricultural practices.`,
        actions,
        disclaimer: 'Regular scouting prevents small issues from escalating into major crop losses.'
      };
    }

    // Immediate action
    actions.push({
      id: `act_imm_${classId}`,
      category: 'immediate',
      title: 'Isolate & Prune Infected Foliage',
      description: disease.treatment.cultural[0] || 'Carefully remove heavily infected leaves during dry weather and dispose away from fields.',
      isUrgent: true
    });

    // Cultural practices
    disease.treatment.cultural.slice(1).forEach((item, idx) => {
      actions.push({
        id: `act_cult_${classId}_${idx}`,
        category: 'cultural',
        title: 'Sanitation & Airflow',
        description: item
      });
    });

    // Organic alternatives
    disease.treatment.organic.forEach((item, idx) => {
      actions.push({
        id: `act_org_${classId}_${idx}`,
        category: 'organic',
        title: 'Organic / Bio-Protection',
        description: item
      });
    });

    // Chemical alternatives
    disease.treatment.chemical.forEach((item, idx) => {
      actions.push({
        id: `act_chem_${classId}_${idx}`,
        category: 'chemical',
        title: 'Chemical Protection Option',
        description: item
      });
    });

    const urgencyLevel =
      disease.severity === 'severe'
        ? 'critical'
        : disease.severity === 'moderate'
        ? 'high'
        : 'moderate';

    return {
      classId,
      diseaseName: disease.displayName,
      crop: disease.crop,
      urgencyLevel,
      headline: `Management Guide for ${disease.displayName}`,
      summary: disease.description,
      actions,
      disclaimer: disease.caution
    };
  }
}
