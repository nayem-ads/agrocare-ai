import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

def evaluate_model(test_path: str = None):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "models", "agrocare_model.keras")
    labels_path = os.path.join(base_dir, "labels.json")
    if test_path is None:
        test_path = os.path.join(base_dir, "datasets", "processed", "test")
    else:
        test_path = os.path.abspath(test_path)
    results_dir = os.path.join(base_dir, "results")

    
    os.makedirs(results_dir, exist_ok=True)
    
    print(f"AgroCare AI Model Evaluator checking files:\nModel: {model_path}\nLabels: {labels_path}\nTest Dir: {test_path}")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file missing at: {model_path}. Please train a model first.")
        
    if not os.path.exists(labels_path):
        raise FileNotFoundError(f"Labels configuration file missing at: {labels_path}")
        
    # 1. Load labels and model
    with open(labels_path, "r") as f:
        labels_dict = json.load(f)
        
    model = tf.keras.models.load_model(model_path)
    print("Real Keras model loaded successfully.")
    
    # Sort classes matching indices keys
    classes_by_idx = [labels_dict[str(i)]["class_name"] for i in range(len(labels_dict))]
    print(f"Classes for evaluation: {classes_by_idx}")
    
    # 2. Test Data Generator
    test_datagen = ImageDataGenerator(rescale=1./255)
    test_gen = test_datagen.flow_from_directory(
        test_path,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        shuffle=False
    )
    
    # Check if generator class list aligns with labels mapping
    gen_classes = list(test_gen.class_indices.keys())
    
    # 3. Predict on Test data
    print("Evaluating predictions on test split...")
    preds = model.predict(test_gen)
    y_pred = np.argmax(preds, axis=1)
    y_true = test_gen.classes
    
    # 4. Compute Metrics
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted')
    
    print("\n" + "=" * 50)
    print(" EVALUATION RESULTS SUMMARY")
    print("=" * 50)
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print("=" * 50 + "\n")
    
    report_dict = classification_report(
        y_true, y_pred,
        labels=list(range(len(gen_classes))),
        target_names=gen_classes,
        output_dict=True
    )

    report_dict["summary"] = {
        "accuracy": acc,
        "weighted_precision": prec,
        "weighted_recall": rec,
        "weighted_f1_score": f1
    }
    
    report_json_path = os.path.join(results_dir, "classification_report.json")
    with open(report_json_path, "w") as f:
        json.dump(report_dict, f, indent=2)
    print(f"Classification report saved to: {report_json_path}")
    
    # 5. Plot and save Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(10, 8))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    plt.colorbar()
    
    tick_marks = np.arange(len(gen_classes))
    plt.xticks(tick_marks, gen_classes, rotation=90)
    plt.yticks(tick_marks, gen_classes)
    
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    
    cm_path = os.path.join(results_dir, "confusion_matrix.png")
    plt.savefig(cm_path)
    plt.close()
    print(f"Confusion matrix image saved to: {cm_path}")
    print("Evaluation completed successfully.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AgroCare AI Model Evaluator")
    parser.add_argument(
        "--dataset",
        default=None,
        help="Path to the test datasets split"
    )
    args = parser.parse_args()
    evaluate_model(args.dataset)

