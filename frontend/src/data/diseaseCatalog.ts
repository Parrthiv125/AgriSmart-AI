import { DiseaseInfo } from '../types/disease';

export const DISEASE_CATALOG: Record<string, DiseaseInfo> = {
  tomato_early_blight: {
    id: 'tomato_early_blight',
    classId: 'tomato_early_blight',
    displayName: 'Early Blight',
    scientificName: 'Alternaria solani',
    crop: 'Tomato',
    isHealthy: false,
    severity: 'moderate',
    description: 'A widespread fungal disease that primarily targets foliage and stems, beginning as circular brown lesions on older bottom leaves.',
    symptoms: [
      'Brown or black spots with distinct concentric rings (target pattern)',
      'Yellowing halo around affected leaf spots',
      'Lower and older leaves wither and drop prematurely',
      'Sunken brown lesions on stems near the soil line'
    ],
    causes: [
      'Fungal spores overwintering in crop debris or contaminated soil',
      'Prolonged leaf moisture and humidity above 80%',
      'Warm daytime temperatures between 24°C and 29°C (75°F - 85°F)',
      'Water splashing soil pathogens onto lower foliage'
    ],
    prevention: [
      'Practice 3 to 4-year crop rotation away from solanaceous crops',
      'Apply organic mulch (straw or plastic) around plant base to prevent soil splash',
      'Water only at the root base using drip irrigation; avoid overhead watering',
      'Stake or trellis plants and prune lower suckers to maximize air circulation'
    ],
    treatment: {
      cultural: [
        'Prune off and safely destroy infected bottom leaves during dry weather',
        'Disinfect pruning shears with 70% alcohol between cuts'
      ],
      organic: [
        'Apply bio-fungicides containing Bacillus subtilis or Trichoderma',
        'Spray copper octanoate or sulfur-based organic protectants early in the season'
      ],
      chemical: [
        'Preventative protectant sprays like Chlorothalonil or Mancozeb before severe spread',
        'Systemic strobilurin or triazole fungicides under severe disease pressure'
      ]
    },
    caution: 'Always follow label rates and pre-harvest intervals (PHI). Consult your local agricultural extension agent before applying synthetic fungicides.'
  },

  tomato_late_blight: {
    id: 'tomato_late_blight',
    classId: 'tomato_late_blight',
    displayName: 'Late Blight',
    scientificName: 'Phytophthora infestans',
    crop: 'Tomato',
    isHealthy: false,
    severity: 'severe',
    description: 'An aggressive water-mold pathogen capable of destroying entire fields within days in cool, wet weather.',
    symptoms: [
      'Large, irregular dark water-soaked lesions on leaves and stems',
      'Delicate white fuzzy mold on leaf undersides during moist mornings',
      'Rapid browning and collapse of entire foliage canopy',
      'Firm, greasy brown rot on green or ripening fruit'
    ],
    causes: [
      'Oomycete pathogen thriving in cool, wet conditions (15°C - 22°C)',
      'Airborne spores traveling over miles in windy, overcast weather',
      'Free water on leaves lasting longer than 8 to 10 hours'
    ],
    prevention: [
      'Plant certified disease-free transplants and certified seed',
      'Select resistant cultivars if available in your growing region',
      'Ensure wide plant spacing for rapid canopy drying after rains'
    ],
    treatment: {
      cultural: [
        'Promptly rogue out and bag severely infected plants; do not compost',
        'Sanitize all stakes and tools at season end'
      ],
      organic: [
        'Fixed copper hydroxide applied preventatively before rain events'
      ],
      chemical: [
        'Targeted oomycete fungicides (e.g., cymoxanil, mandipropamid, dimethomorph)',
        'Rotate chemical modes of action to prevent pathogen resistance'
      ]
    },
    caution: 'Late blight is a community-level threat. Notify neighboring farms if confirmed to coordinate preventative protection.'
  },

  tomato_leaf_mold: {
    id: 'tomato_leaf_mold',
    classId: 'tomato_leaf_mold',
    displayName: 'Leaf Mold',
    scientificName: 'Passalora fulva',
    crop: 'Tomato',
    isHealthy: false,
    severity: 'mild',
    description: 'A common greenhouse and high-tunnel fungal infection thriving in humid, poorly ventilated environments.',
    symptoms: [
      'Pale greenish-yellow indistinct spots on upper leaf surfaces',
      'Velvety olive-green to grayish-brown fungal spores underneath',
      'Leaves curl, turn brown, and drop from bottom upward'
    ],
    causes: [
      'Relative humidity exceeding 85% with limited air exchange',
      'Warm greenhouse conditions (21°C - 24°C)'
    ],
    prevention: [
      'Increase ventilation, side-wall opening, and exhaust fan circulation',
      'Avoid overhead watering and dense plant crowding'
    ],
    treatment: {
      cultural: ['Strip lower infected leaves to improve airflow through the canopy'],
      organic: ['Neem oil or potassium bicarbonate sprays'],
      chemical: ['Fungicides registered for greenhouse use if humidity cannot be lowered']
    },
    caution: 'Check greenhouse heating and ventilation controls to maintain relative humidity below 80%.'
  },

  tomato_septoria_leaf_spot: {
    id: 'tomato_septoria_leaf_spot',
    classId: 'tomato_septoria_leaf_spot',
    displayName: 'Septoria Leaf Spot',
    scientificName: 'Septoria lycopersici',
    crop: 'Tomato',
    isHealthy: false,
    severity: 'moderate',
    description: 'A destructive fungal foliage disease characterized by numerous tiny circular lesions with grayish centers and dark borders.',
    symptoms: [
      'Small, circular spots (1.5 - 3mm) with dark brown margins and gray centers',
      'Tiny black specks (pycnidia fruiting bodies) visible in spot centers with hand lens',
      'Progressive yellowing and defoliation from ground level upward'
    ],
    causes: [
      'Rain-splashed soil fungi surviving in old crop residues and nightshade weeds',
      'Warm wet weather (20°C - 25°C) with persistent leaf wetness'
    ],
    prevention: [
      'Deep mulch around plant bases',
      'Strict eradication of horsenettle and other solanaceous weeds',
      'Minimum 2-year crop rotation'
    ],
    treatment: {
      cultural: ['Remove and destroy infected leaves immediately when first noticed'],
      organic: ['Liquid copper fungicides or sulfur sprays at 7-10 day intervals'],
      chemical: ['Chlorothalonil or copper-based preventative fungicide applications']
    },
    caution: 'Do not work in the fields while foliage is wet to avoid spreading spores between rows.'
  },

  tomato_spider_mites: {
    id: 'tomato_spider_mites',
    classId: 'tomato_spider_mites',
    displayName: 'Two-Spotted Spider Mite',
    scientificName: 'Tetranychus urticae',
    crop: 'Tomato',
    isHealthy: false,
    severity: 'moderate',
    description: 'Microscopic sap-feeding arachnids that colonize leaf undersides, causing stippling and severe moisture stress in hot, dry conditions.',
    symptoms: [
      'Fine pale yellow or white speckling (stippling) on upper leaf surfaces',
      'Fine silky webbing visible on leaf undersides and shoot tips',
      'Leaves become bronze, desiccated, and brittle',
      'Stunted plant vigor during warm drought periods'
    ],
    causes: [
      'Hot, dry, and dusty microclimates (temperatures > 30°C)',
      'Excess nitrogen fertilizer promoting succulent tender growth',
      'Broad-spectrum insecticide sprays killing beneficial predatory mites'
    ],
    prevention: [
      'Keep field perimeter pathways dampened or vegetated to suppress dust',
      'Encourage or release predatory mites (Phytoseiulus persimilis)',
      'Maintain adequate soil moisture during summer heat waves'
    ],
    treatment: {
      cultural: ['Overhead water misting in early morning to dislodge mites and elevate humidity'],
      organic: ['Insecticidal soap, horticultural mineral oil, or azadirachtin (neem extract)'],
      chemical: ['Targeted miticides (e.g., bifenazate or abamectin) specifically sparing beneficials']
    },
    caution: 'Avoid pyrethroid insecticides which often trigger explosive secondary spider mite outbreaks.'
  },

  tomato_target_spot: {
    id: 'tomato_target_spot',
    classId: 'tomato_target_spot',
    displayName: 'Target Spot',
    scientificName: 'Corynespora cassiicola',
    crop: 'Tomato',
    isHealthy: false,
    severity: 'moderate',
    description: 'Fungal leaf and fruit disease producing dark circular spots with distinct concentric rings, common in warm humid climates.',
    symptoms: [
      'Brown lesions with pale brown centers and yellow halos',
      'Concentric target-like rings within leaf lesions',
      'Sunken lesions on green and ripe tomato fruit'
    ],
    causes: ['High relative humidity (85-95%) and warm temperatures (20-28°C)'],
    prevention: ['Adequate plant spacing, trellis staking, and clean field hygiene'],
    treatment: {
      cultural: ['Prune lower leaves to improve airflow'],
      organic: ['Copper fungicides applied preventatively'],
      chemical: ['Registered strobilurin or carboxamide fungicides']
    },
    caution: 'Ensure thorough spray coverage on both upper and lower leaf surfaces.'
  },

  tomato_yellow_leaf_curl_virus: {
    id: 'tomato_yellow_leaf_curl_virus',
    classId: 'tomato_yellow_leaf_curl_virus',
    displayName: 'Yellow Leaf Curl Virus',
    scientificName: 'TYLCV (Begomovirus)',
    crop: 'Tomato',
    isHealthy: false,
    severity: 'severe',
    description: 'A devastating viral disease transmitted by the sweetpotato whitefly (Bemisia tabaci), causing severe stunting and crop loss.',
    symptoms: [
      'Severe upward curling and cupping of leaf margins',
      'Pronounced yellowing (chlorosis) of young expanding leaves',
      'Marked stunting of internodes and bushiness',
      'Flower drop with little to no fruit development'
    ],
    causes: [
      'Transmission by whiteflies feeding on virus reservoir weeds or infected plants',
      'Warm weather encouraging rapid whitefly population growth'
    ],
    prevention: [
      'Plant TYLCV-resistant tomato varieties (look for TY resistant seed)',
      'Install fine insect exclusion netting (50-mesh) over nursery seedlings',
      'Use yellow sticky cards for early whitefly monitoring'
    ],
    treatment: {
      cultural: ['Rogue out and destroy infected plants immediately upon symptom detection'],
      organic: ['Apply insecticidal soap or horticultural oil to suppress whiteflies'],
      chemical: ['Targeted systemic insecticides for vector management in nursery beds']
    },
    caution: 'There is no cure for viral infections once a plant is infected. Focus exclusively on vector control and resistant varieties.'
  },

  tomato_mosaic_virus: {
    id: 'tomato_mosaic_virus',
    classId: 'tomato_mosaic_virus',
    displayName: 'Tomato Mosaic Virus',
    scientificName: 'ToMV (Tobamovirus)',
    crop: 'Tomato',
    isHealthy: false,
    severity: 'moderate',
    description: 'A very persistent mechanically transmitted virus causing mottled foliage and distorted growth.',
    symptoms: [
      'Mottled light green and dark green mosaic patterns on foliage',
      'Distorted, fern-like or curled leaves',
      'Uneven fruit ripening and internal brown browning of fruit walls'
    ],
    causes: [
      'Mechanical transmission through handling, tools, pruning, and seed coats',
      'Virus particles survive for years in soil and dry plant debris'
    ],
    prevention: [
      'Use certified virus-free seed or heat-treated seed',
      'Wash hands with soap and water before handling tomato seedlings',
      'Disinfect tools in 10% household bleach or 20% non-fat milk solution'
    ],
    treatment: {
      cultural: ['Remove and destroy infected plants; do not compost'],
      organic: ['Preventative milk sprays during transplanting to reduce contact transmission'],
      chemical: ['No chemical treatments exist for plant viruses']
    },
    caution: 'Smokers should wash hands thoroughly with soap before touching plants as tobacco products can harbor related viruses.'
  },

  tomato_healthy: {
    id: 'tomato_healthy',
    classId: 'tomato_healthy',
    displayName: 'Healthy Crop',
    scientificName: 'Solanum lycopersicum',
    crop: 'Tomato',
    isHealthy: true,
    severity: 'none',
    description: 'The tomato foliage displays vibrant, uniform green color without detectable lesions, chlorosis, or pest infestation.',
    symptoms: ['Lush, uniform green foliage', 'Sturdy stems and healthy turgid leaves', 'Active vegetative and floral growth'],
    causes: ['Balanced soil fertility, adequate sunlight, and proper irrigation management'],
    prevention: ['Continue routine field scouting and maintain consistent drip irrigation schedule'],
    treatment: {
      cultural: ['Maintain clean mulch and regular suckering for optimal airflow'],
      organic: ['Continue standard organic fertilization and compost tea drenches'],
      chemical: ['No chemical intervention required']
    },
    caution: 'Keep monitoring weekly for early signs of seasonal pests or weather-related stress.'
  },

  potato_early_blight: {
    id: 'potato_early_blight',
    classId: 'potato_early_blight',
    displayName: 'Early Blight',
    scientificName: 'Alternaria solani',
    crop: 'Potato',
    isHealthy: false,
    severity: 'moderate',
    description: 'Fungal leaf disease in potatoes that accelerates plant senescence and reduces tuber yield and size.',
    symptoms: [
      'Dark brown to black angular spots with concentric target-like rings',
      'Yellow chlorotic rings bordering leaf lesions',
      'Premature defoliation of lower canopy reducing tuber bulking'
    ],
    causes: ['Alternating wet and dry periods, stressed plants, and nitrogen deficiency'],
    prevention: ['Ensure adequate, balanced fertility and avoid moisture stress'],
    treatment: {
      cultural: ['Destroy haulms (vines) before harvest to prevent tuber contamination'],
      organic: ['Copper sulfate or copper hydroxide preventative sprays'],
      chemical: ['Apply protectant fungicides (Mancozeb, Chlorothalonil) starting at tuber initiation']
    },
    caution: 'Do not harvest tubers while foliage is wet or green to prevent tuber rot in storage.'
  },

  potato_late_blight: {
    id: 'potato_late_blight',
    classId: 'potato_late_blight',
    displayName: 'Late Blight',
    scientificName: 'Phytophthora infestans',
    crop: 'Potato',
    isHealthy: false,
    severity: 'severe',
    description: 'The historic Irish potato famine pathogen that rapidly kills foliage and infects tubers with dry, corky rot.',
    symptoms: [
      'Water-soaked dark lesions spreading rapidly across leaves and stems',
      'White fluffy mold visible on leaf undersides in humid conditions',
      'Entire canopy can collapse within 7 to 10 days',
      'Tubers develop sunken purplish-brown skin and dry granular rot inside'
    ],
    causes: ['Cool temperatures (10-20°C) with persistent fog, rain, or dew'],
    prevention: ['Use certified seed potatoes and plant resistant cultivars'],
    treatment: {
      cultural: ['Kill vines 2-3 weeks before harvest to prevent spores from reaching tubers'],
      organic: ['Preventative copper sprays applied prior to anticipated rainy spells'],
      chemical: ['Specific anti-oomycete systemic fungicides according to local blight forecasts']
    },
    caution: 'Inspect cull piles and volunteer potatoes; destroy them immediately as primary inoculum sources.'
  },

  potato_healthy: {
    id: 'potato_healthy',
    classId: 'potato_healthy',
    displayName: 'Healthy Crop',
    scientificName: 'Solanum tuberosum',
    crop: 'Potato',
    isHealthy: true,
    severity: 'none',
    description: 'Strong, vigorous potato foliage exhibiting rich green pigment and healthy canopy structure without disease indicators.',
    symptoms: ['Uniform dark green canopy', 'Healthy flowering and sturdy stems', 'Absence of foliar blemishes'],
    causes: ['Optimal hilling, adequate potassium and nitrogen, good drainage'],
    prevention: ['Maintain hilling around plant bases to shield developing tubers from sunlight and blight spores'],
    treatment: {
      cultural: ['Maintain consistent soil moisture throughout the tuber bulking period'],
      organic: ['Routine foliar micronutrient feeding as needed'],
      chemical: ['No chemical treatments required']
    },
    caution: 'Maintain regular scouting especially following periods of heavy rain.'
  },

  corn_common_rust: {
    id: 'corn_common_rust',
    classId: 'corn_common_rust',
    displayName: 'Common Rust',
    scientificName: 'Puccinia sorghi',
    crop: 'Corn (Maize)',
    isHealthy: false,
    severity: 'moderate',
    description: 'Fungal disease producing cinnamon-brown pustules on both upper and lower corn leaf surfaces, reducing photosynthesis.',
    symptoms: [
      'Small, circular to elongated cinnamon-brown pustules',
      'Pustules rupture leaf epidermis exposing powdery brown spores',
      'Present on both leaf surfaces, often in bands across the leaf blade'
    ],
    causes: [
      'Spores carried northward by storm systems and high winds',
      'Cool to moderate temperatures (16-25°C) with high humidity'
    ],
    prevention: ['Plant rust-resistant hybrid corn varieties suited for your region'],
    treatment: {
      cultural: ['Maintain optimal crop nutrition to help plants tolerate foliage loss'],
      organic: ['Not economically viable on broad-acre corn; select resistant hybrids'],
      chemical: ['Triazole or strobilurin fungicides if disease appears prior to tasseling and threshold is exceeded']
    },
    caution: 'Scout upper leaves around tasseling (VT to R1 stages) to assess need for fungicide application.'
  },

  corn_gray_leaf_spot: {
    id: 'corn_gray_leaf_spot',
    classId: 'corn_gray_leaf_spot',
    displayName: 'Gray Leaf Spot',
    scientificName: 'Cercospora zeae-maydis',
    crop: 'Corn (Maize)',
    isHealthy: false,
    severity: 'moderate',
    description: 'Fungal disease producing distinct rectangular lesions bounded by leaf veins, common in minimum-tillage continuous corn systems.',
    symptoms: [
      'Tan to gray rectangular lesions strictly delimited by parallel leaf veins',
      'Lesions measure 1 to 5 cm in length and 2 to 4 mm wide',
      'Severe blighting and premature death of entire leaves'
    ],
    causes: ['High surface crop residue, extended periods of dew, and temperatures above 27°C'],
    prevention: ['Crop rotation away from corn for at least one season and residue management'],
    treatment: {
      cultural: ['Rotate with soybeans or non-host broadleaf crops'],
      organic: ['Resistant hybrid selection is the principal control'],
      chemical: ['Fungicide applications applied at VT-R1 stage if lesions reach ear leaf']
    },
    caution: 'Evaluate stalk integrity at maturity as early leaf loss increases risk of stalk lodging.'
  },

  corn_northern_leaf_blight: {
    id: 'corn_northern_leaf_blight',
    classId: 'corn_northern_leaf_blight',
    displayName: 'Northern Corn Leaf Blight',
    scientificName: 'Exserohilum turcicum',
    crop: 'Corn (Maize)',
    isHealthy: false,
    severity: 'moderate',
    description: 'Causes large cigar-shaped grayish-green lesions on corn foliage, severely inhibiting grain fill during late reproductive stages.',
    symptoms: [
      'Large, elliptical or cigar-shaped lesions (3 - 15 cm long)',
      'Lesions turn grayish-green to tan with dark sporulation zones',
      'Blighting starts on lower leaves and progresses upward'
    ],
    causes: ['Moderate temperatures (18-27°C) with prolonged rain and wet foliage'],
    prevention: ['Plant hybrids containing specific Ht resistance genes and rotate fields'],
    treatment: {
      cultural: ['Tillage to bury infected corn residue where appropriate for soil conservation'],
      organic: ['Genetic resistance is the primary management strategy'],
      chemical: ['Fungicide application at tassel stage if disease pressure is high']
    },
    caution: 'Check hybrid resistance ratings before purchasing seed for the next growing season.'
  },

  corn_healthy: {
    id: 'corn_healthy',
    classId: 'corn_healthy',
    displayName: 'Healthy Crop',
    scientificName: 'Zea mays',
    crop: 'Corn (Maize)',
    isHealthy: true,
    severity: 'none',
    description: 'Vigorous corn stand with robust dark green leaves, sturdy stalks, and normal vegetative or reproductive development.',
    symptoms: ['Deep green leaves without blemishes or pustules', 'Uniform stand height and strong stalk base', 'Healthy tassel and silk development'],
    causes: ['Optimal planting depth, balanced soil fertility (N-P-K), and adequate moisture'],
    prevention: ['Maintain recommended plant population density and weed control'],
    treatment: {
      cultural: ['Side-dress nitrogen at V4-V6 stage based on soil test recommendations'],
      organic: ['Regular scouting for fall armyworms or corn borers'],
      chemical: ['No intervention required']
    },
    caution: 'Monitor soil moisture during pollination (silking) when corn is most sensitive to moisture deficit.'
  },

  apple_scab: {
    id: 'apple_scab',
    classId: 'apple_scab',
    displayName: 'Apple Scab',
    scientificName: 'Venturia inaequalis',
    crop: 'Apple',
    isHealthy: false,
    severity: 'moderate',
    description: 'The most economically significant fungal disease of apples worldwide, causing scabby lesions on leaves and fruit.',
    symptoms: [
      'Olive-green to velvety dark brown spots on leaves with feathered margins',
      'Leaves may distort, curl, and drop prematurely',
      'Crusty, corky brown scabs on developing fruit causing cracking'
    ],
    causes: ['Fungus overwintering in fallen leaves on the orchard floor', 'Wet spring weather during bud break and blossom'],
    prevention: ['Shred or rake fallen leaves in autumn or spray urea to accelerate leaf decomposition'],
    treatment: {
      cultural: ['Open canopy pruning in winter to allow rapid leaf drying after rain'],
      organic: ['Sulfur or lime-sulfur sprays applied before anticipated rain events'],
      chemical: ['Captan, Dithianon, or sterol-inhibitor fungicides according to Mills infection periods']
    },
    caution: 'Timely sprays during the primary infection period (tight cluster to petal fall) are critical.'
  },

  apple_black_rot: {
    id: 'apple_black_rot',
    classId: 'apple_black_rot',
    displayName: 'Black Rot',
    scientificName: 'Botryosphaeria obtusa',
    crop: 'Apple',
    isHealthy: false,
    severity: 'moderate',
    description: 'A fungal disease causing frog-eye leaf spots, limb cankers, and firm brown-black rot on ripening fruit.',
    symptoms: [
      'Frog-eye leaf spots: small purple spots enlarging with tan centers and dark purple borders',
      'Sunken cankers on branches with cracked bark',
      'Fruit develops firm brown rings that turn jet black with tiny pimples'
    ],
    causes: ['Dead wood, mummified fruit left hanging from previous season, and wounded bark'],
    prevention: ['Remove all mummified fruit during winter dormant pruning', 'Prune out dead and cankered branches 15 cm below visible margins'],
    treatment: {
      cultural: ['Burn or bury all pruned infected wood'],
      organic: ['Copper sprays during late dormant stage'],
      chemical: ['Broad-spectrum fungicides like Captan or Thiophanate-methyl']
    },
    caution: 'Control fire blight and insect damage, as wounds provide infection courts for black rot.'
  },

  apple_cedar_rust: {
    id: 'apple_cedar_rust',
    classId: 'apple_cedar_rust',
    displayName: 'Cedar Apple Rust',
    scientificName: 'Gymnosporangium juniperi-virginianae',
    crop: 'Apple',
    isHealthy: false,
    severity: 'mild',
    description: 'An alternating rust fungus requiring both apple trees and eastern red cedar (juniper) to complete its two-year life cycle.',
    symptoms: [
      'Bright yellow-orange spots on upper leaf surfaces',
      'Small raised orange dots on spot centers',
      'Tube-like fungal structures (aecia) protruding from lower leaf surfaces'
    ],
    causes: ['Airborne spores blown from cedar galls during warm spring rains', 'Proximity to wild eastern red cedar trees (Juniperus virginiana)'],
    prevention: ['Plant rust-immune or resistant apple cultivars (e.g., Enterprise, Liberty)', 'Remove eastern red cedar trees within 500 meters of the orchard where feasible'],
    treatment: {
      cultural: ['Inspect and remove galls from nearby ornamental junipers before spring'],
      organic: ['Sulfur sprays timed to pink bud through petal fall'],
      chemical: ['Myclobutanil or DMI fungicides applied during the cedar spore-release window']
    },
    caution: 'Chemical sprays are only effective if applied before spores penetrate leaf tissue.'
  },

  apple_healthy: {
    id: 'apple_healthy',
    classId: 'apple_healthy',
    displayName: 'Healthy Crop',
    scientificName: 'Malus domestica',
    crop: 'Apple',
    isHealthy: true,
    severity: 'none',
    description: 'Orchard foliage and young fruit are clean, exhibiting vibrant green coloration, crisp margins, and strong shoot extension.',
    symptoms: ['Clean, glossy green leaves without spots or curling', 'Smooth fruit skin free of blemishes or russeting', 'Strong annual shoot growth'],
    causes: ['Balanced orchard floor management, good canopy sunlight penetration, and proactive pest monitoring'],
    prevention: ['Continue regular orchard scouting and maintain drip irrigation during dry spells'],
    treatment: {
      cultural: ['Perform summer pruning of watersprouts to maintain canopy airflow'],
      organic: ['Apply kaolin clay sprays for solar protection if summer heat is extreme'],
      chemical: ['No intervention required']
    },
    caution: 'Inspect fruit regularly for codling moth or fruit fly stings as harvest approaches.'
  },

  grape_black_rot: {
    id: 'grape_black_rot',
    classId: 'grape_black_rot',
    displayName: 'Black Rot',
    scientificName: 'Guignardia bidwellii',
    crop: 'Grape',
    isHealthy: false,
    severity: 'severe',
    description: 'A serious fungal disease that attacks all green vine tissue and transforms lush grape clusters into hard, shriveled black mummies.',
    symptoms: [
      'Small, circular reddish-brown spots on leaves surrounded by dark margins',
      'Tiny black fruiting bodies (pycnidia) arranged in rings inside leaf lesions',
      'Infected berries rapidly rot, shrivel, and turn into hard black mummies'
    ],
    causes: ['Rainy weather and warm temperatures (21-27°C) during bloom and early berry set', 'Mummified berries hanging on vines or on vineyard floor'],
    prevention: ['Strict sanitation: remove all mummified fruit clusters during dormant pruning', 'Canopy management to allow rapid drying of clusters'],
    treatment: {
      cultural: ['Shoot thinning and leaf pulling around fruit zone after bloom'],
      organic: ['Preventative copper and lime-sulfur sprays applied early in the season'],
      chemical: ['Fungicides (Mancozeb, Ziram, or myclobutanil) applied from pre-bloom to 4 weeks post-bloom']
    },
    caution: 'Berries are most susceptible from bloom until they reach pea size (about 5-6 weeks after bloom).'
  },

  grape_esca: {
    id: 'grape_esca',
    classId: 'grape_esca',
    displayName: 'Esca (Black Measles)',
    scientificName: 'Phaeoacremonium & Fomitiporia',
    crop: 'Grape',
    isHealthy: false,
    severity: 'moderate',
    description: 'A complex trunk disease caused by wood-decaying fungi, leading to characteristic tiger-stripe foliage and spotted fruit.',
    symptoms: [
      'Tiger-stripe pattern: yellowing and browning between leaf veins with green margins remaining along veins',
      'Dark purplish specks (measles) on berry skin',
      'Sudden collapse (apoplexy) of entire vine during hot dry spells'
    ],
    causes: ['Fungi entering through large pruning wounds during wet winter conditions', 'Older vineyards (typically 8+ years old)'],
    prevention: ['Delay pruning until late winter when wound healing is faster', 'Apply wound sealant or pruning paste to large cuts'],
    treatment: {
      cultural: ['Curettage (surgical removal of necrotic trunk wood) or trunk renewal from suckers'],
      organic: ['Trichoderma-based wound protectants applied immediately after pruning'],
      chemical: ['No systemic chemical cures exist for established wood infection']
    },
    caution: 'Prune infected vines last and sanitize pruning shears in 70% alcohol between vines.'
  },

  grape_leaf_blight: {
    id: 'grape_leaf_blight',
    classId: 'grape_leaf_blight',
    displayName: 'Leaf Blight (Isariopsis)',
    scientificName: 'Pseudocercospora vitis',
    crop: 'Grape',
    isHealthy: false,
    severity: 'mild',
    description: 'Late-season fungal foliage spot causing premature leaf fall and reduced winter vine hardiness.',
    symptoms: [
      'Irregular brown angular spots on leaves in mid to late summer',
      'Dark olive velvety growth on the underside of spots',
      'Premature defoliation affecting fruit ripening'
    ],
    causes: ['High humidity, dense unmanaged canopies, and warm rainy late-summer weather'],
    prevention: ['Maintain open canopy through shoot positioning and leaf removal'],
    treatment: {
      cultural: ['Remove excessive shoots and weeds beneath the trellis'],
      organic: ['Copper hydroxide sprays applied after veraison if weather is wet'],
      chemical: ['Broad-spectrum protectant fungicides applied post-bloom']
    },
    caution: 'Ensure grape bunches receive adequate dappled sunlight for optimal sugar accumulation.'
  },

  grape_healthy: {
    id: 'grape_healthy',
    classId: 'grape_healthy',
    displayName: 'Healthy Crop',
    scientificName: 'Vitis vinifera',
    crop: 'Grape',
    isHealthy: true,
    severity: 'none',
    description: 'Vigorous grapevine canopy with healthy green leaves, strong tendrils, and clean developing fruit bunches.',
    symptoms: ['Clean, uniform green leaves without spots or necrotic margins', 'Intact, smooth berries in well-formed bunches', 'Active shoot tips and healthy tendrils'],
    causes: ['Balanced vine vigor, adequate soil drainage, and good trellis management'],
    prevention: ['Maintain shoot tucking and selective leaf pulling in the fruiting zone'],
    treatment: {
      cultural: ['Continue regular vine canopy maintenance and weed mowing between vine rows'],
      organic: ['Preventative elemental sulfur dust for mildew prophylaxis if regionally indicated'],
      chemical: ['No chemical intervention required']
    },
    caution: 'Scout regularly for early signs of powdery mildew under shaded leaf clusters.'
  },

  pepper_bacterial_spot: {
    id: 'pepper_bacterial_spot',
    classId: 'pepper_bacterial_spot',
    displayName: 'Bacterial Spot',
    scientificName: 'Xanthomonas campestris pv. vesicatoria',
    crop: 'Pepper Bell',
    isHealthy: false,
    severity: 'moderate',
    description: 'A serious bacterial pathogen causing water-soaked leaf spots, leaf drop, and rough scab-like lesions on pepper fruit.',
    symptoms: [
      'Small, circular to irregular water-soaked spots on foliage',
      'Spots turn brown with pale centers on upper surface and dark centers below',
      'Severe defoliation exposing fruit to sunscald',
      'Raised, rough scab-like spots on green and colored bell peppers'
    ],
    causes: ['Contaminated seed or transplants', 'Warm rainy weather and splashing water from rain or overhead sprinklers'],
    prevention: ['Use certified disease-free, hot-water-treated pepper seed', 'Plant resistant bell pepper hybrids (races 1-10 resistance)'],
    treatment: {
      cultural: ['Avoid working in pepper fields when plants are wet', 'Use plastic mulch and drip irrigation exclusively'],
      organic: ['Fixed copper mixed with mancozeb or bio-bactericides (Bacillus)'],
      chemical: ['Copper bactericides; monitor for local copper-resistant strains']
    },
    caution: 'Do not use overhead sprinkler irrigation in pepper cultivation if bacterial spot is present in the region.'
  },

  pepper_healthy: {
    id: 'pepper_healthy',
    classId: 'pepper_healthy',
    displayName: 'Healthy Crop',
    scientificName: 'Capsicum annuum',
    crop: 'Pepper Bell',
    isHealthy: true,
    severity: 'none',
    description: 'Sturdy pepper plants with broad dark green foliage, healthy white blossoms, and firm unblemished bell peppers.',
    symptoms: ['Glossy, dark green leaves free of spots or wilting', 'Firm, crisp fruit without blemishes or sunscald', 'Steady flower set and branch vigor'],
    causes: ['Consistent soil moisture, warm temperatures (21-28°C), and well-drained fertile loam'],
    prevention: ['Stake or cage pepper plants to support heavy fruit load and prevent soil contact'],
    treatment: {
      cultural: ['Maintain consistent soil moisture to prevent blossom end rot (calcium deficiency)'],
      organic: ['Side-dress with well-rotted organic compost or fish emulsion'],
      chemical: ['No chemical intervention required']
    },
    caution: 'Keep soil evenly moist, especially during hot spells when fruit is developing.'
  },

  rice_brown_spot: {
    id: 'rice_brown_spot',
    classId: 'rice_brown_spot',
    displayName: 'Brown Spot',
    scientificName: 'Bipolaris oryzae',
    crop: 'Rice',
    isHealthy: false,
    severity: 'moderate',
    description: 'A fungal disease affecting seedlings, leaves, and panicles, historically associated with nutrient-deficient or drought-stressed paddies.',
    symptoms: [
      'Small circular to oval brown spots with gray or whitish centers',
      'Yellow halos surrounding leaf spots on seedlings and mature leaves',
      'Discolored and shriveled grains with reduced milling quality'
    ],
    causes: ['Nutrient-poor soils (especially low silicon, potassium, and nitrogen)', 'Drought stress or unflooded paddy conditions'],
    prevention: ['Correct soil nutritional deficiencies; apply potassium and silicate fertilizers', 'Use certified seed and hot water seed treatment (53-54°C for 10 min)'],
    treatment: {
      cultural: ['Maintain continuous shallow water depth in the paddy; avoid drying out'],
      organic: ['Seed treatment with Trichoderma viride or Pseudomonas fluorescens'],
      chemical: ['Foliar fungicides (azoxystrobin, propiconazole) applied at tillering and boot stages']
    },
    caution: 'Ensure balanced fertilization: brown spot is strongly correlated with potassium and nitrogen malnutrition.'
  },

  wheat_rust: {
    id: 'wheat_rust',
    classId: 'wheat_rust',
    displayName: 'Leaf Rust (Brown Rust)',
    scientificName: 'Puccinia triticina',
    crop: 'Wheat',
    isHealthy: false,
    severity: 'moderate',
    description: 'An airborne fungal rust that produces reddish-orange pustules scattered on upper wheat leaves, causing grain shriveling.',
    symptoms: [
      'Small, circular to oval reddish-orange pustules (uredinia)',
      'Pustules scattered randomly across the upper leaf surface',
      'Dusty orange spores readily rub off on fingers or clothing',
      'Leaves turn yellow and senesce prematurely during grain filling'
    ],
    causes: ['Airborne spores transported by regional wind currents', 'Mild temperatures (15-22°C) with dew or high moisture lasting >6 hours'],
    prevention: ['Plant rust-resistant wheat varieties recommended by local agricultural extension', 'Eradicate volunteer wheat plants over summer to break green bridge'],
    treatment: {
      cultural: ['Avoid early autumn planting in winter wheat areas to prevent early infection'],
      organic: ['Resistant variety selection is the only practical broad-acre method'],
      chemical: ['Triazole or strobilurin fungicides applied before flag leaf is damaged (Zadoks 39 stage)']
    },
    caution: 'Protecting the flag leaf is paramount: the flag leaf provides over 75% of the grain filling carbohydrates.'
  }
};

export const ALL_DISEASE_CLASSES = Object.values(DISEASE_CATALOG);
export const TOTAL_CLASSES_COUNT = ALL_DISEASE_CLASSES.length; // Exactly 28
