import os
import json
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

def evaluate_model(test_path: str):
    """
    Evaluates the trained infection model against the test split.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "models", "agrocare_infection_model.keras")
    labels_path = os.path.join(base_dir, "infection_labels.json")
    metadata_path = os.path.join(base_dir, "models", "infection_model_metadata.json")
    results_dir = os.path.join(base_dir, "results")
    
    os.makedirs(results_dir, exist_ok=True)
    
    print(f"Infection Model Evaluator checking files:\nModel: {model_path}\nLabels: {labels_path}\nTest Dir: {test_path}")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file missing at: {model_path}. Please train a model first.")
    if not os.path.exists(labels_path):
        raise FileNotFoundError(f"Labels file missing at: {labels_path}.")
    if not os.path.exists(test_path):
        raise FileNotFoundError(f"Test split directory missing at: {test_path}.")
        
    with open(labels_path, "r") as f:
        labels_dict = json.load(f)
    categories = [labels_dict[k]["class_name"] for k in sorted(labels_dict.keys(), key=int)]
    
    # Load metadata for model_family
    model_family = "mobilenet"
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                meta = json.load(f)
                model_family = meta.get("model_family", "mobilenet")
        except Exception:
            pass
            
    if model_family == "efficientnet":
        from tensorflow.keras.applications.efficientnet import preprocess_input
    else:
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
        
    print("Loading Keras infection model...")
    model = tf.keras.models.load_model(model_path)
    print("Model loaded successfully.")
    
    test_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)
    test_gen = test_datagen.flow_from_directory(
        test_path,
        target_size=(224, 224),
        batch_size=16,
        class_mode='categorical',
        shuffle=False
    )
    
    print("Evaluating predictions on test split...")
    predictions = model.predict(test_gen)
    
    # Ensure softmax applied if logits
    is_softmax = np.isclose(np.sum(predictions[0]), 1.0, atol=1e-3)
    if not is_softmax:
        exp_preds = np.exp(predictions - np.max(predictions, axis=1, keepdims=True))
        predictions = exp_preds / np.sum(exp_preds, axis=1, keepdims=True)
        
    y_pred = np.argmax(predictions, axis=1)
    y_true = test_gen.classes
    
    acc = float(accuracy_score(y_true, y_pred))
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
    prec, rec, f1 = float(prec), float(rec), float(f1)
    
    # Bias detection: check if one class is predicted > 80% of the time
    total_preds = len(y_pred)
    model_bias_detected = False
    if total_preds > 0:
        counts = np.bincount(y_pred, minlength=len(categories))
        for c_idx, count in enumerate(counts):
            ratio = count / total_preds
            if ratio > 0.8:
                print(f"[WARNING] Model is highly biased! Class '{categories[c_idx]}' was predicted {ratio*100:.2f}% of the time.")
                model_bias_detected = True
                
    print("\n" + "=" * 50)
    print(" EVALUATION RESULTS SUMMARY")
    print("=" * 50)
    print(f"Accuracy:            {acc:.4f}")
    print(f"Precision:           {prec:.4f}")
    print(f"Recall:              {rec:.4f}")
    print(f"F1-Score:            {f1:.4f}")
    print(f"Model Bias Detected: {model_bias_detected}")
    print("=" * 50 + "\n")
    
    report_dict = classification_report(
        y_true, y_pred,
        labels=list(range(len(categories))),
        target_names=categories,
        output_dict=True,
        zero_division=0
    )
    report_dict["summary"] = {
        "accuracy": acc,
        "weighted_precision": prec,
        "weighted_recall": rec,
        "weighted_f1_score": f1,
        "model_bias_detected": model_bias_detected
    }
    
    report_json_path = os.path.join(results_dir, "infection_classification_report.json")
    with open(report_json_path, "w") as f:
        json.dump(report_dict, f, indent=2)
    print(f"Classification report saved to: {report_json_path}")
    
    # Save evaluation summary
    eval_summary = {
        "accuracy": acc,
        "weighted_precision": prec,
        "weighted_recall": rec,
        "weighted_f1_score": f1,
        "model_bias_detected": model_bias_detected
    }
    eval_summary_path = os.path.join(results_dir, "infection_evaluation_summary.json")
    with open(eval_summary_path, "w") as f:
        json.dump(eval_summary, f, indent=2)
    print(f"Evaluation summary saved to: {eval_summary_path}")
    
    # Update infection_model_metadata.json with bias status
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                meta = json.load(f)
            meta["model_bias_detected"] = model_bias_detected
            meta["evaluation_accuracy"] = acc
            meta["evaluation_f1_score"] = f1
            with open(metadata_path, "w") as f:
                json.dump(meta, f, indent=2)
            print("Model metadata file updated with evaluation metrics.")
        except Exception as e:
            print(f"Error updating metadata: {e}")
            
    # Plot and save Confusion Matrix
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(categories))))
    plt.figure(figsize=(10, 8))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Infection Model Confusion Matrix')
    plt.colorbar()
    tick_marks = np.arange(len(categories))
    plt.xticks(tick_marks, categories, rotation=45)
    plt.yticks(tick_marks, categories)
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()
    cm_path = os.path.join(results_dir, "infection_confusion_matrix.png")
    plt.savefig(cm_path)
    plt.close()
    print(f"Confusion matrix image saved to: {cm_path}")
    print("Evaluation completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgroCare AI Infection Model Evaluator")
    parser.add_argument(
        "--dataset",
        default="ml/datasets/processed_infection/test",
        help="Path to the test datasets split"
    )
    args = parser.parse_args()
    evaluate_model(args.dataset)
