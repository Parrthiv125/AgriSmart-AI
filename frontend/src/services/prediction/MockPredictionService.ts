import { PredictionService } from './PredictionService';
import { PredictionResult, ConfidenceLevel } from '../../types/prediction';
import { SAMPLE_IMAGES } from '../../data/mockData';
import { DISEASE_CATALOG, ALL_DISEASE_CLASSES } from '../../data/diseaseCatalog';
import { historyService } from '../history';

export class MockPredictionService implements PredictionService {
  private predictions: Map<string, PredictionResult> = new Map();

  async predict(imageFile: File | Blob, cropHint?: string): Promise<PredictionResult> {
    // Realistic simulated ML inference delay (1200ms)
    await new Promise((res) => setTimeout(res, 1200));

    // Create object URL for the uploaded leaf image
    let previewUrl: string;
    try {
      previewUrl = URL.createObjectURL(imageFile);
    } catch {
      previewUrl = SAMPLE_IMAGES.tomatoHealthy;
    }

    // Check if filename contains hint keywords for deterministic testing
    const fileName = (imageFile as File).name?.toLowerCase() || '';
    let selectedClassId = 'tomato_early_blight';
    let confidence = 0.942;
    let confidenceLevel: ConfidenceLevel = 'high';

    if (fileName.includes('healthy')) {
      selectedClassId = 'potato_healthy';
      confidence = 0.965;
      confidenceLevel = 'high';
    } else if (fileName.includes('low') || fileName.includes('blur') || fileName.includes('uncertain')) {
      selectedClassId = 'tomato_leaf_mold';
      confidence = 0.485;
      confidenceLevel = 'low';
    } else if (fileName.includes('corn') || fileName.includes('rust')) {
      selectedClassId = 'corn_common_rust';
      confidence = 0.738;
      confidenceLevel = 'medium';
    } else if (cropHint) {
      const match = ALL_DISEASE_CLASSES.find(
        (d) => d.crop.toLowerCase().includes(cropHint.toLowerCase()) && !d.isHealthy
      );
      if (match) selectedClassId = match.classId;
    }

    const disease = DISEASE_CATALOG[selectedClassId] || DISEASE_CATALOG.tomato_early_blight;
    const predictionId = `pred_${Date.now()}`;

    let explanation = '';
    if (confidenceLevel === 'low') {
      explanation = `The scan detected patterns loosely resembling ${disease.displayName}, but confidence is low (${Math.round(confidence * 100)}%). Foliage lighting or focus may be insufficient for a definitive diagnosis.`;
    } else if (disease.isHealthy) {
      explanation = `No fungal, bacterial, or viral symptoms detected. Foliage displays robust chlorophyll distribution and intact cell structure. Crop is in good health.`;
    } else {
      explanation = `Characteristic symptoms of ${disease.displayName} detected with ${Math.round(confidence * 100)}% confidence. Lesion morphology and chlorosis match known pathology indicators.`;
    }

    const prediction: PredictionResult = {
      predictionId,
      crop: disease.crop,
      disease: {
        classId: disease.classId,
        name: confidenceLevel === 'low' ? `Uncertain: Possible ${disease.displayName}` : disease.displayName,
        scientificName: disease.scientificName,
        isHealthy: disease.isHealthy
      },
      confidence,
      confidenceLevel,
      imageUrl: previewUrl,
      explanation,
      recommendation: {
        title: disease.isHealthy
          ? 'Maintain Preventive Care & Soil Moisture'
          : confidenceLevel === 'low'
          ? 'Retake Photo in Clear Natural Sunlight'
          : `Immediate Mitigation for ${disease.displayName}`,
        summary: disease.isHealthy
          ? 'Continue routine inspection and recommended crop nourishment.'
          : confidenceLevel === 'low'
          ? 'Do not apply chemical interventions while diagnosis is inconclusive.'
          : disease.prevention[0] || 'Prune affected foliage and apply registered crop protection.',
        actions: disease.isHealthy
          ? ['Maintain consistent drip irrigation.', 'Inspect underside of foliage weekly.']
          : confidenceLevel === 'low'
          ? [
              'Take a photo in bright, indirect sunlight.',
              'Hold camera 15-20 cm from leaf to prevent blur.',
              'Focus on a single leaf with the clearest spot patterns.'
            ]
          : [
              ...(disease.treatment.cultural.slice(0, 2)),
              ...(disease.treatment.organic.slice(0, 1))
            ]
      },
      createdAt: new Date().toISOString(),
      modelName: 'EfficientNet-B2 Model 2 (Field-Adapted)'
    };

    // Store in memory
    this.predictions.set(predictionId, prediction);

    // Also record in history service
    try {
      historyService.addHistoryItem({
        id: `hist_${Date.now()}`,
        predictionId,
        crop: prediction.crop,
        diseaseName: prediction.disease.name,
        classId: prediction.disease.classId,
        confidence: prediction.confidence,
        confidenceLevel: prediction.confidenceLevel,
        status: disease.isHealthy ? 'healthy' : confidenceLevel === 'low' ? 'uncertain' : 'diseased',
        imageUrl: previewUrl,
        createdAt: prediction.createdAt,
        notes: `Analyzed via Model 2 (Field-Adapted)`
      });
    } catch {
      // ignore history tracking errors
    }

    return prediction;
  }

  async getPredictionById(predictionId: string): Promise<PredictionResult | null> {
    await new Promise((res) => setTimeout(res, 100));
    return this.predictions.get(predictionId) || null;
  }
}
