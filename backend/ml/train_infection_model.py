import os
import json
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.utils.class_weight import compute_class_weight

def train_infection_model(dataset_dir: str, model_arch: str, epochs: int, batch_size: int):
    """
    Trains the Infection Category classifier model.
    """
    print(f"Training parameters:\nDataset Dir: {dataset_dir}\nModel Architecture: {model_arch}\nEpochs: {epochs}\nBatch Size: {batch_size}")
    
    train_dir = os.path.join(dataset_dir, "train")
    val_dir = os.path.join(dataset_dir, "validation")
    
    # 1. Setup Preprocessing Function based on model family
    if model_arch.lower() == "efficientnet":
        from tensorflow.keras.applications.efficientnet import preprocess_input
        model_family = "efficientnet"
    else:
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
        model_family = "mobilenet"
        
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    val_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)
    
    train_gen = train_datagen.flow_from_directory(
        train_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=True
    )
    
    val_gen = val_datagen.flow_from_directory(
        val_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False
    )
    
    num_classes = len(train_gen.class_indices)
    class_indices = train_gen.class_indices
    print(f"Detected class indices mapping: {class_indices}")
    
    # 2. Build Model
    if model_family == "efficientnet":
        print("Using EfficientNetB0 base weights...")
        base_model = tf.keras.applications.EfficientNetB0(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
    else:
        print("Using MobileNetV2 base weights...")
        base_model = tf.keras.applications.MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
    base_model.trainable = False
    
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
    
    # Calculate class weights
    classes = np.unique(train_gen.classes)
    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=classes,
        y=train_gen.classes
    )
    class_weight_dict = dict(zip(classes, class_weights))
    print(f"Calculated class weights: {class_weight_dict}")
    
    # Paths Setup
    base_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.abspath(os.path.join(base_dir, "models"))
    results_dir = os.path.abspath(os.path.join(base_dir, "results"))
    
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)
    
    keras_path = os.path.join(models_dir, "agrocare_infection_model.keras")
    h5_path = os.path.join(models_dir, "agrocare_infection_model.h5")
    
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
        ModelCheckpoint(filepath=keras_path, monitor='val_loss', save_best_only=True),
        ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-6)
    ]
    
    # 3. Fit
    print(f"Beginning training pipeline for {epochs} epochs...")
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=epochs,
        class_weight=class_weight_dict,
        callbacks=callbacks
    )
    
    # Save H5 fallback
    print(f"Exporting legacy H5 fallback model to: {h5_path}")
    model.save(h5_path)
    
    # 4. Save infection_labels.json exactly as required
    category_labels_dict = {}
    categories_clean = {
        "Fungal_Infection": "Fungal Infection",
        "Bacterial_Infection": "Bacterial Infection",
        "Viral_Disease": "Viral Disease",
        "Pest_Damage": "Pest Damage",
        "Nutrient_Deficiency": "Nutrient Deficiency",
        "Healthy_Leaf": "Healthy Leaf"
    }
    
    for label_name, idx in class_indices.items():
        category_labels_dict[str(idx)] = {
            "class_name": label_name,
            "infection_category": categories_clean.get(label_name, label_name.replace("_", " ")),
            "is_healthy": (label_name == "Healthy_Leaf")
        }
        
    labels_path = os.path.abspath(os.path.join(base_dir, "infection_labels.json"))
    with open(labels_path, "w") as f:
        json.dump(category_labels_dict, f, indent=2)
    print(f"Infection labels exported to: {labels_path}")
    
    # Save infection_class_indices.json in models folder
    class_indices_path = os.path.join(models_dir, "infection_class_indices.json")
    with open(class_indices_path, "w") as f:
        json.dump(category_labels_dict, f, indent=2)
    print(f"Infection class indices exported to: {class_indices_path}")
    
    # 5. Save model metadata
    metadata = {
        "model_version": "agrocare_infection_model_v1",
        "model_type": "infection_category",
        "number_of_classes": num_classes,
        "trained_categories": [
            "Fungal Infection",
            "Bacterial Infection",
            "Viral Disease",
            "Pest Damage",
            "Nutrient Deficiency",
            "Healthy Leaf"
        ],
        "crop_filter_required": False,
        "model_family": model_family
    }

    metadata_path = os.path.join(models_dir, "infection_model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata exported to: {metadata_path}")
    
    # 6. Save plots
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='train_acc')
    plt.plot(history.history['val_accuracy'], label='val_acc')
    plt.title('Accuracy')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='train_loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.title('Loss')
    plt.legend()
    
    plot_path = os.path.join(results_dir, "infection_training_history.png")
    plt.savefig(plot_path)
    plt.close()
    print(f"Training history curves saved to: {plot_path}")
    
    # 7. Save metrics JSON
    metrics = {
        "final_loss": float(history.history['loss'][-1]),
        "final_accuracy": float(history.history['accuracy'][-1]),
        "final_val_loss": float(history.history['val_loss'][-1]),
        "final_val_accuracy": float(history.history['val_accuracy'][-1])
    }
    metrics_path = os.path.join(results_dir, "infection_training_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Training metrics saved to: {metrics_path}")
    
    print("Training process finished successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgroCare AI Infection Category Model Trainer")
    parser.add_argument("--dataset", default="ml/datasets/processed_infection", help="Processed dataset folder")
    parser.add_argument("--model", default="mobilenet", choices=["mobilenet", "efficientnet"], help="Base model architecture")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Training batch size")
    args = parser.parse_args()
    train_infection_model(args.dataset, args.model, args.epochs, args.batch_size)
