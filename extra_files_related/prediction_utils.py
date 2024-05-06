# prediction_utils.py

import cv2
import numpy as np
from keras.models import load_model
import os


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Load the model globally
model = load_model("model_keras/new_model.h5", compile=False)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

def get_prediction(img_path):
    global model

    # Read the image
    img = cv2.imread(img_path)
    
    # Resize the image
    img = cv2.resize(img, dsize=(200, 200))

    # Preprocess the image
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)

    # Get prediction
    prediction = model.predict(img)

    return prediction.tolist()

def subprocess_function(img_path):
    prediction = get_prediction(img_path)
    return prediction
