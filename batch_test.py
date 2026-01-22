import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

# 1. Configuration
MODEL_PATH = "models/landmark_model.h5"
TEST_FOLDER = "test_images/"
IMG_SIZE = (224, 224)  # Ensure this matches your model's input size
CLASS_NAMES = ["Eiffel Tower", "Taj Mahal", "London Bridge"] # Change to your actual labels

# 2. Load the trained model
model = tf.keras.models.load_model(MODEL_PATH)

print(f"--- Starting Batch Test on {TEST_FOLDER} ---")

# 3. Loop through every image in the folder
for filename in os.listdir(TEST_FOLDER):
    if filename.endswith((".jpg", ".png", ".jpeg")):
        img_path = os.path.join(TEST_FOLDER, filename)
        
        # Preprocessing (CRITICAL STEP)
        img = image.load_img(img_path, target_size=IMG_SIZE)
        img_array = image.img_to_array(img)
        img_array = img_array / 255.0  # Normalization matching your training
        img_array = np.expand_dims(img_array, axis=0) # Add batch dimension

        # Run Prediction
        predictions = model.predict(img_array, verbose=0)
        score = np.max(predictions[0])
        class_idx = np.argmax(predictions[0])
        label = CLASS_NAMES[class_idx]

        print(f"📷 Image: {filename} | Predicted: {label} | Confidence: {score:.2%}")