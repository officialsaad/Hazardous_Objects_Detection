import cv2
import numpy as np
import os
import tensorflow as tf
from keras.models import load_model
import multiprocessing

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Load the model globally
global model
model = load_model("model_keras/new_model.h5", compile=False)
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy'])

def get_prediction(img_path):
    # Use the globally defined model
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

# Function to be executed by the multiprocessing
def multiprocessing_function(img_path, result_queue):
    prediction = get_prediction(img_path)
    result_queue.put(prediction)

if __name__ == "__main__":
    img_path = "prediction_images/fire/fire1.jpg"
    result_queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=multiprocessing_function, args=(img_path, result_queue))
    process.start()
    process.join()
    result = result_queue.get()
    print("Prediction from multiprocessing:", result)
