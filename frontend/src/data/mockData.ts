import { User } from '../types/auth';
import { PredictionResult } from '../types/prediction';
import { HistoryItem } from '../types/history';
import { DashboardData } from '../types/dashboard';

// Clean inline SVG leaf representations for mock image display
export const SAMPLE_IMAGES = {
  tomatoEarlyBlight: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%"><rect width="400" height="300" fill="%232b5329"/><path d="M70 240 C120 180 180 80 340 50 C320 160 260 250 140 270 Z" fill="%23437a38"/><circle cx="180" cy="140" r="28" fill="%235c3c1e" opacity="0.85"/><circle cx="180" cy="140" r="16" fill="%233e2713" opacity="0.9"/><circle cx="180" cy="140" r="8" fill="%238a6237"/><circle cx="230" cy="180" r="20" fill="%235c3c1e" opacity="0.8"/><circle cx="230" cy="180" r="10" fill="%233e2713"/><circle cx="270" cy="110" r="18" fill="%235c3c1e" opacity="0.75"/><circle cx="270" cy="110" r="9" fill="%233e2713"/><path d="M120 260 Q180 160 330 60" stroke="%23284f1f" stroke-width="4" fill="none"/></svg>`,
  tomatoHealthy: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%"><rect width="400" height="300" fill="%231a3818"/><path d="M60 250 C110 170 170 70 340 40 C330 170 270 250 130 280 Z" fill="%233ea42e"/><path d="M110 260 Q180 150 330 50" stroke="%2328731d" stroke-width="4" fill="none"/><path d="M180 150 Q150 120 130 130" stroke="%2328731d" stroke-width="2.5" fill="none"/><path d="M220 120 Q240 90 270 95" stroke="%2328731d" stroke-width="2.5" fill="none"/><path d="M250 90 Q220 70 200 75" stroke="%2328731d" stroke-width="2.5" fill="none"/></svg>`,
  cornRust: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%"><rect width="400" height="300" fill="%231e331b"/><path d="M40 280 C100 200 180 60 360 30 C320 180 240 270 100 290 Z" fill="%235b8c38"/><circle cx="160" cy="140" r="6" fill="%23b85d19"/><circle cx="175" cy="135" r="5" fill="%23b85d19"/><circle cx="190" cy="150" r="7" fill="%23b85d19"/><circle cx="210" cy="120" r="6" fill="%23b85d19"/><circle cx="225" cy="115" r="5" fill="%23b85d19"/><circle cx="240" cy="130" r="6" fill="%23b85d19"/><circle cx="260" cy="100" r="6" fill="%23b85d19"/><circle cx="280" cy="80" r="5" fill="%23b85d19"/></svg>`,
  potatoHealthy: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%"><rect width="400" height="300" fill="%23163319"/><path d="M80 230 C120 150 190 70 330 60 C320 180 250 250 140 260 Z" fill="%23389e34"/><path d="M120 240 Q190 140 320 70" stroke="%23226a20" stroke-width="4" fill="none"/></svg>`,
  grapeBlackRot: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%"><rect width="400" height="300" fill="%23223820"/><path d="M70 250 C110 160 170 80 340 50 C320 170 250 260 130 270 Z" fill="%23487c32"/><circle cx="190" cy="140" r="22" fill="%23211510"/><circle cx="240" cy="170" r="16" fill="%23211510"/><circle cx="260" cy="110" r="14" fill="%23211510"/></svg>`,
  lowConfidenceLeaf: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="100%" height="100%"><rect width="400" height="300" fill="%233a3830"/><path d="M100 240 C140 180 180 100 310 80 C290 170 240 230 160 250 Z" fill="%235a664e" filter="blur(2px)"/><circle cx="200" cy="160" r="30" fill="%234a4035" opacity="0.6"/><text x="200" y="270" fill="%23e2e8f0" font-size="14" text-anchor="middle" font-family="sans-serif">Sample Leaf Image (Blurry/Low Light)</text></svg>`
};

export const MOCK_CURRENT_USER: User = {
  id: 'usr_farmer_01',
  name: 'Ramesh Patel',
  email: 'ramesh.farmer@agrismart.ai',
  farmName: 'Sunrise Agricultural Farm',
  location: 'Nashik District, Maharashtra',
  crops: ['Tomato', 'Potato', 'Corn (Maize)', 'Grape'],
  createdAt: '2026-08-15T09:30:00Z'
};

export const MOCK_PREDICTIONS: Record<string, PredictionResult> = {
  pred_001: {
    predictionId: 'pred_001',
    crop: 'Tomato',
    disease: {
      classId: 'tomato_early_blight',
      name: 'Early Blight',
      scientificName: 'Alternaria solani',
      isHealthy: false
    },
    confidence: 0.942,
    confidenceLevel: 'high',
    imageUrl: SAMPLE_IMAGES.tomatoEarlyBlight,
    explanation: 'Distinct concentric brown target rings detected on lower leaf surface with chlorotic yellow halos. Classic early blight fungal infection signature.',
    recommendation: {
      title: 'Prune Infected Leaves & Apply Protectant Fungicide',
      summary: 'Immediate action needed to stop fungal spores from spreading up the plant canopy.',
      actions: [
        'Prune and destroy infected lower leaves immediately using sanitized shears.',
        'Avoid all overhead sprinkler irrigation; water strictly at soil base.',
        'Apply organic copper-based fungicide or bio-fungicide (Bacillus subtilis) within 48 hours.',
        'Mulch soil around plants with clean straw to block rain splash.'
      ]
    },
    createdAt: '2026-09-14T10:15:00Z',
    modelName: 'EfficientNet-B2 Model 1'
  },

  pred_002: {
    predictionId: 'pred_002',
    crop: 'Potato',
    disease: {
      classId: 'potato_healthy',
      name: 'Healthy Crop',
      scientificName: 'Solanum tuberosum',
      isHealthy: true
    },
    confidence: 0.968,
    confidenceLevel: 'high',
    imageUrl: SAMPLE_IMAGES.potatoHealthy,
    explanation: 'Leaf exhibits vibrant chlorophyll pigmentation, intact leaf margins, and zero characteristic fungal or bacterial lesions. Foliage is in prime health.',
    recommendation: {
      title: 'Maintain Current Cultural Practices',
      summary: 'Your potato crop is vigorous and disease-free. Continue proactive preventative care.',
      actions: [
        'Continue consistent drip irrigation to support tuber development.',
        'Maintain hilling around base to keep developing tubers protected from sunlight.',
        'Scout fields weekly, especially following humid or rainy weather.'
      ]
    },
    createdAt: '2026-09-13T14:40:00Z',
    modelName: 'EfficientNet-B2 Model 1'
  },

  pred_003: {
    predictionId: 'pred_003',
    crop: 'Corn (Maize)',
    disease: {
      classId: 'corn_common_rust',
      name: 'Common Rust',
      scientificName: 'Puccinia sorghi',
      isHealthy: false
    },
    confidence: 0.735,
    confidenceLevel: 'medium',
    imageUrl: SAMPLE_IMAGES.cornRust,
    explanation: 'Scattered cinnamon-brown pustules detected across upper leaf blade. Symptoms are consistent with moderate common rust infection.',
    recommendation: {
      title: 'Monitor Rust Spread & Assess Flag Leaf',
      summary: 'Moderate rust presence. Treatment depends on growth stage and proximity to tasseling.',
      actions: [
        'Inspect upper ear leaves and flag leaves to see if pustules are moving upward.',
        'Check local weather forecast; hot dry weather (>30°C) naturally suppresses rust fungus.',
        'Consult extension specialist before chemical application if corn is past blister stage (R2).'
      ]
    },
    createdAt: '2026-09-12T09:20:00Z',
    modelName: 'EfficientNet-B2 Model 1'
  },

  pred_004: {
    predictionId: 'pred_004',
    crop: 'Tomato',
    disease: {
      classId: 'tomato_leaf_mold',
      name: 'Uncertain: Possible Leaf Mold',
      scientificName: 'Passalora fulva',
      isHealthy: false
    },
    confidence: 0.485,
    confidenceLevel: 'low',
    imageUrl: SAMPLE_IMAGES.lowConfidenceLeaf,
    explanation: 'Visual features are ambiguous due to low lighting and angle. The AI detected slight discoloration, but confidence is insufficient for a confirmed diagnosis.',
    recommendation: {
      title: 'Retake Photo in Bright Natural Light',
      summary: 'Confidence is low (< 60%). Do not apply chemical treatments based on this scan.',
      actions: [
        'Take a new photo in clear daytime lighting without shadows.',
        'Hold camera 15-20 cm away and ensure the leaf fills 70% of the frame.',
        'Turn leaf over if spots are mainly on the underside to capture underside symptoms.'
      ]
    },
    createdAt: '2026-09-11T16:05:00Z',
    modelName: 'EfficientNet-B2 Model 1'
  }
};

export const MOCK_HISTORY: HistoryItem[] = [
  {
    id: 'hist_001',
    predictionId: 'pred_001',
    crop: 'Tomato',
    diseaseName: 'Early Blight',
    classId: 'tomato_early_blight',
    confidence: 0.942,
    confidenceLevel: 'high',
    status: 'diseased',
    imageUrl: SAMPLE_IMAGES.tomatoEarlyBlight,
    createdAt: '2026-09-14T10:15:00Z',
    notes: 'South plot near boundary fence'
  },
  {
    id: 'hist_002',
    predictionId: 'pred_002',
    crop: 'Potato',
    diseaseName: 'Healthy Crop',
    classId: 'potato_healthy',
    confidence: 0.968,
    confidenceLevel: 'high',
    status: 'healthy',
    imageUrl: SAMPLE_IMAGES.potatoHealthy,
    createdAt: '2026-09-13T14:40:00Z',
    notes: 'Row 4 main field'
  },
  {
    id: 'hist_003',
    predictionId: 'pred_003',
    crop: 'Corn (Maize)',
    diseaseName: 'Common Rust',
    classId: 'corn_common_rust',
    confidence: 0.735,
    confidenceLevel: 'medium',
    status: 'diseased',
    imageUrl: SAMPLE_IMAGES.cornRust,
    createdAt: '2026-09-12T09:20:00Z',
    notes: 'East terrace'
  },
  {
    id: 'hist_004',
    predictionId: 'pred_004',
    crop: 'Tomato',
    diseaseName: 'Uncertain: Possible Leaf Mold',
    classId: 'tomato_leaf_mold',
    confidence: 0.485,
    confidenceLevel: 'low',
    status: 'uncertain',
    imageUrl: SAMPLE_IMAGES.lowConfidenceLeaf,
    createdAt: '2026-09-11T16:05:00Z',
    notes: 'Evening scan in low light'
  }
];

export const MOCK_DASHBOARD_DATA: DashboardData = {
  metrics: {
    totalScans: 18,
    healthyCropsCount: 11,
    diseasedCropsCount: 6,
    uncertainCount: 1,
    scansThisWeek: 7,
    healthyPercentage: 61
  },
  latestPrediction: MOCK_PREDICTIONS.pred_001,
  recentScans: MOCK_HISTORY,
  commonCrops: [
    { crop: 'Tomato', count: 8 },
    { crop: 'Potato', count: 5 },
    { crop: 'Corn (Maize)', count: 3 },
    { crop: 'Grape', count: 2 }
  ]
};
