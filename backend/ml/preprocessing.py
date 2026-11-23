import numpy as np
from PIL import Image, ImageOps
import io

def preprocess_image(image_bytes: bytes, target_size=(224, 224), model_family="mobilenet") -> np.ndarray:
    """
    Loads an image, corrects EXIF orientation, converts to RGB, resizes, and normalizes deterministically.
    Random transformations (crop, rotation, brightness) are strictly omitted.
    """
    image = Image.open(io.BytesIO(image_bytes))
    
    # 1. Correct EXIF orientation issues
    image = ImageOps.exif_transpose(image)
    
    # 2. Convert to RGB to handle alpha channels and formats consistently
    if image.mode != "RGB":
        image = image.convert("RGB")
        
    # 3. Deterministic resize
    image = image.resize(target_size, Image.Resampling.BILINEAR)
    
    # 4. Standardize normalization based on model family
    img_array = np.array(image, dtype=np.float32)
    
    if model_family == "mobilenet":
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
        img_array = preprocess_input(img_array)
    elif model_family == "efficientnet":
        from tensorflow.keras.applications.efficientnet import preprocess_input
        img_array = preprocess_input(img_array)
    else:
        img_array = img_array / 255.0
        
    img_array = np.expand_dims(img_array, axis=0)
    return img_array
