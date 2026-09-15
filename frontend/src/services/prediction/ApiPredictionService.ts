import { PredictionService } from './PredictionService';
import { PredictionResult, ConfidenceLevel, PredictionDisease } from '../../types/prediction';
import { DiseaseInfo } from '../../types/disease';
import { predictionApi, BackendPredictionResponse } from '../api/predictionApi';
import { DISEASE_CATALOG, ALL_DISEASE_CLASSES } from '../../data/diseaseCatalog';
import { historyService } from '../history';

export class ApiPredictionService implements PredictionService {
  private predictions: Map<string, PredictionResult> = new Map();

  async predict(imageFile: File | Blob, cropHint?: string): Promise<PredictionResult> {
    // Create preview URL for the uploaded image
    let previewUrl = '';
    try {
      previewUrl = URL.createObjectURL(imageFile);
    } catch {
      previewUrl = '';
    }

    // Call live backend /predict endpoint
    const response: BackendPredictionResponse = await predictionApi.predict(imageFile, cropHint);

    const classLabel = response.class_label || response.disease || 'Plant — Leaf Observation';
    const confidence = typeof response.confidence === 'number' ? response.confidence : 0.0;

    // Determine confidence level
    let confidenceLevel: ConfidenceLevel = 'high';
    if (response.confidence_level) {
      const lvl = response.confidence_level.toLowerCase();
      if (lvl.includes('low')) confidenceLevel = 'low';
      else if (lvl.includes('med')) confidenceLevel = 'medium';
      else confidenceLevel = 'high';
    } else {
      if (confidence >= 0.80) confidenceLevel = 'high';
      else if (confidence >= 0.60) confidenceLevel = 'medium';
      else confidenceLevel = 'low';
    }

    // Parse crop and disease name from class_label (e.g., "Tomato — Early Blight", "Corn — Northern Leaf Blight")
    const parts = classLabel.split(/—|-|___/).map((s) => s.trim());
    const crop = parts[0] || (cropHint || 'Plant');
    const diseaseName = parts.length > 1 ? parts.slice(1).join(' — ') : classLabel;
    const isHealthy = classLabel.toLowerCase().includes('healthy');

    // Attempt fuzzy match with frontend disease catalog
    const normalizedKey = classLabel
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '');

    let matchedCatalog: DiseaseInfo | undefined = DISEASE_CATALOG[normalizedKey];

    if (!matchedCatalog) {
      // Try finding by matching disease displayName and crop
      matchedCatalog = ALL_DISEASE_CLASSES.find((item) => {
        const itemCropMatch = item.crop.toLowerCase().includes(crop.toLowerCase()) || crop.toLowerCase().includes(item.crop.toLowerCase());
        const itemNameMatch = classLabel.toLowerCase().includes(item.displayName.toLowerCase()) ||
          item.displayName.toLowerCase().includes(diseaseName.toLowerCase());
        return itemCropMatch && itemNameMatch;
      });
    }

    if (!matchedCatalog) {
      // Fallback: match by crop and health status
      matchedCatalog = ALL_DISEASE_CLASSES.find((item) => {
        const itemCropMatch = item.crop.toLowerCase().includes(crop.toLowerCase());
        return itemCropMatch && (item.isHealthy === isHealthy);
      });
    }

    const predictionId = `pred_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;

    // Build disease info
    const disease: PredictionDisease = {
      classId: matchedCatalog?.classId || normalizedKey,
      name: confidenceLevel === 'low' ? `Uncertain: Possible ${matchedCatalog?.displayName || diseaseName}` : (matchedCatalog?.displayName || diseaseName),
      scientificName: matchedCatalog?.scientificName,
      isHealthy: isHealthy
    };

    // Explanation
    let explanation = '';
    if (response.low_confidence_warning) {
      explanation = response.low_confidence_warning;
    } else if (confidenceLevel === 'low') {
      explanation = `The model detected characteristics loosely resembling ${disease.name}, but confidence is low (${Math.round(confidence * 100)}%). Foliage lighting or focus may be insufficient for a definitive diagnosis.`;
    } else if (isHealthy) {
      explanation = `No fungal, bacterial, or viral disease symptoms detected. Foliage shows healthy tissue characteristics and intact cellular morphology. Crop is in good health.`;
    } else if (matchedCatalog?.description) {
      explanation = matchedCatalog.description;
    } else {
      explanation = `Characteristic symptoms of ${disease.name} detected with ${Math.round(confidence * 100)}% confidence using Model 2 field-adapted inference.`;
    }

    // Recommendations & Precautions
    const actions: string[] = [];
    if (response.precaution) {
      const precautionLines = response.precaution.split(/\.\s+/).map(s => s.trim().replace(/\.$/, '')).filter(Boolean);
      actions.push(...precautionLines);
    }

    if (matchedCatalog) {
      if (isHealthy) {
        if (matchedCatalog.prevention && matchedCatalog.prevention.length > 0) {
          actions.push(...matchedCatalog.prevention.slice(0, 2));
        }
      } else {
        if (matchedCatalog.treatment?.cultural) {
          actions.push(...matchedCatalog.treatment.cultural.slice(0, 2));
        }
        if (matchedCatalog.treatment?.organic) {
          actions.push(...matchedCatalog.treatment.organic.slice(0, 1));
        }
      }
    }

    if (actions.length === 0) {
      if (isHealthy) {
        actions.push('Maintain consistent drip irrigation.', 'Inspect underside of foliage weekly.');
      } else if (confidenceLevel === 'low') {
        actions.push(
          'Take a photo in bright, indirect natural sunlight.',
          'Hold camera 15-20 cm from leaf to prevent blur.',
          'Focus on a single leaf with the clearest symptoms.'
        );
      } else {
        actions.push(
          'Prune off and safely dispose of affected foliage.',
          'Avoid overhead irrigation to reduce canopy moisture.',
          'Consult local agricultural extension service for targeted treatment.'
        );
      }
    }

    const recommendationTitle = isHealthy
      ? 'Maintain Preventive Care & Crop Nutrition'
      : confidenceLevel === 'low'
      ? 'Retake Photo in Clear Natural Sunlight'
      : `Recommended Action Plan for ${disease.name}`;

    const recommendationSummary = response.precaution || (
      isHealthy
        ? 'Continue routine inspection and recommended crop nourishment.'
        : confidenceLevel === 'low'
        ? 'Do not apply chemical interventions while diagnosis is inconclusive.'
        : (matchedCatalog?.prevention?.[0] || 'Prune affected foliage and practice integrated pest management.')
    );

    const prediction: PredictionResult = {
      predictionId,
      crop: matchedCatalog?.crop || crop,
      disease,
      confidence,
      confidenceLevel,
      imageUrl: previewUrl,
      explanation,
      recommendation: {
        title: recommendationTitle,
        summary: recommendationSummary,
        actions: Array.from(new Set(actions))
      },
      createdAt: new Date().toISOString(),
      modelName: 'EfficientNet-B2 Model 2 (Field-Adapted)'
    };

    // Cache in-memory
    this.predictions.set(predictionId, prediction);

    // Also persist in sessionStorage if in browser environment
    try {
      if (typeof window !== 'undefined' && window.sessionStorage) {
        sessionStorage.setItem(`agrismart_pred_${predictionId}`, JSON.stringify(prediction));
      }
    } catch {
      // ignore storage errors
    }

    // Record in history
    try {
      historyService.addHistoryItem({
        id: `hist_${Date.now()}`,
        predictionId,
        crop: prediction.crop,
        diseaseName: prediction.disease.name,
        classId: prediction.disease.classId,
        confidence: prediction.confidence,
        confidenceLevel: prediction.confidenceLevel,
        status: isHealthy ? 'healthy' : confidenceLevel === 'low' ? 'uncertain' : 'diseased',
        imageUrl: previewUrl,
        createdAt: prediction.createdAt,
        notes: `Analyzed via Model 2 (Field-Adapted) — ${(confidence * 100).toFixed(1)}%`
      });
    } catch {
      // ignore history tracking errors
    }

    return prediction;
  }

  async getPredictionById(predictionId: string): Promise<PredictionResult | null> {
    if (this.predictions.has(predictionId)) {
      return this.predictions.get(predictionId)!;
    }

    try {
      if (typeof window !== 'undefined' && window.sessionStorage) {
        const stored = sessionStorage.getItem(`agrismart_pred_${predictionId}`);
        if (stored) {
          const parsed = JSON.parse(stored) as PredictionResult;
          this.predictions.set(predictionId, parsed);
          return parsed;
        }
      }
    } catch {
      // ignore storage errors
    }

    return null;
  }
}
