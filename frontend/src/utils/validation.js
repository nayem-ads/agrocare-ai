/**
 * Validates the prediction/diagnosis result object for logical consistency and correctness.
 * @param {Object} result - The response payload from predict or report details API.
 * @returns {boolean} - True if valid, false if inconsistent or invalid.
 */
export function validatePredictionResult(result) {
  if (!result) return false;

  const confidenceScore = result.confidence_score;
  const topPredictions = result.top_predictions;
  const diseaseName = result.disease_name;
  const diseaseType = result.disease_type;
  const isHealthy = result.is_healthy;
  const treatment = result.treatment_advice || '';
  const modelLoaded = result.model_loaded;
  const predictionSource = result.prediction_source;

  // 1. confidence_score is number
  if (typeof confidenceScore !== 'number') {
    console.error("Validation Error: confidence_score is not a number", confidenceScore);
    return false;
  }

  // 2. top_predictions is array
  if (!Array.isArray(topPredictions)) {
    console.error("Validation Error: top_predictions is not an array", topPredictions);
    return false;
  }

  // 3. disease_name exists
  if (!diseaseName) {
    console.error("Validation Error: disease_name is missing");
    return false;
  }

  // 4. disease_type exists
  if (!diseaseType) {
    console.error("Validation Error: disease_type is missing");
    return false;
  }

  // 5. if is_healthy=false, treatment should not say “No disease detected”
  const isHealthyName = diseaseName.toLowerCase() === 'healthy leaf' || diseaseName.toLowerCase() === 'healthy' || (result.infection_category && result.infection_category.toLowerCase() === 'healthy leaf');
  if (!isHealthy && !isHealthyName && treatment.toLowerCase().includes('no disease detected')) {
    console.error("Validation Error: Inconsistent advisory. is_healthy is false, but treatment says 'No disease detected'.");
    return false;
  }

  // 6. if model_loaded=true, prediction_source must be “Real AI Model”
  if (modelLoaded && predictionSource !== 'Real AI Model') {
    console.error("Validation Error: Inconsistent model source. model_loaded is true, but source is not 'Real AI Model'.", predictionSource);
    return false;
  }

  // 7. check infection_category validity if provided
  const validCategories = [
    "Fungal Infection",
    "Bacterial Infection",
    "Viral Disease",
    "Pest Damage",
    "Nutrient Deficiency",
    "Healthy Leaf"
  ];
  if (result.infection_category && !validCategories.includes(result.infection_category)) {
    console.error("Validation Error: Invalid infection_category:", result.infection_category);
    return false;
  }

  // Warning check: if model_loaded=true but confidence_score is missing or 0
  if (modelLoaded && confidenceScore === 0) {
    console.warn("Prediction confidence is invalid (0). Please check backend inference.");
  }

  return true;
}

