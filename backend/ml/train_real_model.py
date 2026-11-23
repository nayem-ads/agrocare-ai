import os
import json
import argparse
import matplotlib
matplotlib.use('Agg') # Disable interactive window rendering
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

def check_gpu_availability():
    """
    Checks and prints available computing devices (CPU/GPU).
    """
    gpus = tf.config.list_physical_devices('GPU')
    print("=" * 60)
    print(" DEVICE DIAGNOSTICS")
    print("=" * 60)
    if gpus:
        print(f"GPU device detected: {gpus}")
        print("Training will run with GPU/MPS acceleration.")
    else:
        print("No GPU detected. Training will fall back to CPU.")
        print("WARNING: Training may be slow on CPU.")
    print("=" * 60 + "\n")

def parse_class_name(folder_name: str) -> dict:
    """
    Parses crop, disease, and infection details from directory name.
    """
    parts = folder_name.split("_")
    crop_name = parts[0]
    rest = " ".join(parts[1:])
    
    is_healthy = "healthy" in folder_name.lower() or "health" in folder_name.lower()
    
    if is_healthy:
        disease_name = "Healthy Leaf"
        disease_type = "Healthy"
    else:
        disease_name = rest.title()
        rest_lower = rest.lower()
        if "bacterial" in rest_lower:
            disease_type = "Bacterial infection"
        elif any(w in rest_lower for w in ["virus", "mosaic", "curl", "tungro"]):
            disease_type = "Viral plant disease"
        elif "pest" in rest_lower:
            disease_type = "Pest damage"
        elif "deficiency" in rest_lower:
            disease_type = "Nutrient deficiency"
        elif any(w in rest_lower for w in ["blight", "mold", "mildew", "rust", "anthracnose", "spot", "blast", "scab", "rot"]):
            disease_type = "Fungal infection"
        else:
            disease_type = "Fungal infection"
            
    return {
        "class_name": folder_name,
        "crop_name": crop_name.title(),
        "disease_name": disease_name,
        "disease_type": disease_type,
        "is_healthy": is_healthy
    }

def train_model(dataset_dir: str, model_type: str, epochs: int, batch_size: int):
    # Detect acceleration
    check_gpu_availability()
    
    train_path = os.path.join(dataset_dir, "train")
    val_path = os.path.join(dataset_dir, "validation")
    
    # 1. Setup Generators (Augment only training, not validation/inference)
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    train_gen = train_datagen.flow_from_directory(
        train_path,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=True
    )
    
    val_gen = val_datagen.flow_from_directory(
        val_path,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False
    )
    
    # Resolve class indices map
    class_indices = train_gen.class_indices
    num_classes = len(class_indices)
    print(f"Detected class mappings: {class_indices}")
    
    # 2. Build Transfer Learning Model
    input_shape = (224, 224, 3)
    if model_type.lower() == "efficientnet":
        print("Initializing EfficientNetB0 base architecture...")
        base_model = tf.keras.applications.EfficientNetB0(
            weights='imagenet',
            include_top=False,
            input_shape=input_shape
        )
    else:
        print("Initializing MobileNetV2 base architecture...")
        base_model = tf.keras.applications.MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=input_shape
        )
        
    base_model.trainable = False  # Freeze base feature extractor
    
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-3),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # 3. Callbacks
    models_dir = os.path.abspath(os.path.join(dataset_dir, "..", "..", "models"))
    os.makedirs(models_dir, exist_ok=True)
    best_keras_path = os.path.join(models_dir, "agrocare_model.keras")
    best_h5_path = os.path.join(models_dir, "agrocare_model.h5")

    
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
        ModelCheckpoint(filepath=best_keras_path, monitor='val_loss', save_best_only=True),
        ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-6)
    ]
    
    # 4. Train Model
    print(f"Beginning training pipeline for {epochs} epochs...")
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=epochs,
        callbacks=callbacks
    )
    
    # Save best model to fallback .h5 format as well
    print(f"Exporting fallback H5 model to: {best_h5_path}")
    model.save(best_h5_path)
    
    # 5. Export labels.json
    labels_dict = {}
    # Build class list matching generator index keys
    for label_name, idx in class_indices.items():
        meta = parse_class_name(label_name)
        labels_dict[str(idx)] = meta
        
    labels_output_path = os.path.abspath(os.path.join(dataset_dir, "..", "..", "labels.json"))
    with open(labels_output_path, "w") as f:
        json.dump(labels_dict, f, indent=2)
    print(f"Class labels dictionary exported to: {labels_output_path}")

    
    # 6. Save model metadata
    metadata = {
        "model_version": "agrocare_model_v1",
        "model_type": model_type,
        "classes_count": num_classes,
        "input_shape": [224, 224, 3],
        "trained_classes": list(class_indices.keys())
    }
    metadata_path = os.path.join(models_dir, "model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Model metadata exported to: {metadata_path}")
    
    # 7. Export training plots
    results_dir = os.path.abspath(os.path.join(dataset_dir, "..", "..", "results"))
    os.makedirs(results_dir, exist_ok=True)

    
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='train_acc')
    plt.plot(history.history['val_accuracy'], label='val_acc')
    plt.title('Accuracy curves')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='train_loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.title('Loss curves')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    
    history_img_path = os.path.join(results_dir, "training_history.png")
    plt.savefig(history_img_path)
    plt.close()
    print(f"Training history curves saved to: {history_img_path}")
    
    # 8. Export training metrics json
    final_metrics = {
        "train_accuracy": float(history.history['accuracy'][-1]),
        "val_accuracy": float(history.history['val_accuracy'][-1]),
        "train_loss": float(history.history['loss'][-1]),
        "val_loss": float(history.history['val_loss'][-1])
    }
    metrics_path = os.path.join(results_dir, "training_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(final_metrics, f, indent=2)
    print(f"Training metrics summary saved to: {metrics_path}")
    print("Training process finished successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgroCare AI Real Model Trainer")
    parser.add_argument(
        "--dataset",
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "datasets", "processed")),
        help="Path to the split datasets directory"
    )
    parser.add_argument(
        "--model",
        choices=["efficientnet", "mobilenet"],
        default="efficientnet",
        help="Base feature extractor model architecture"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=15,
        help="Number of epochs to train"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for training"
    )
    
    args = parser.parse_args()
    train_model(args.dataset, args.model, args.epochs, args.batch_size)
