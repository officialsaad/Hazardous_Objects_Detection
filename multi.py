import cv2
import numpy as np
import os
import tensorflow as tf
from keras.models import load_model
import multiprocessing
from plyer import notification
import threading
import time
import winsound
from datetime import datetime

from database_connection import DatabaseConnection
from tkinter import messagebox


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Load the model globally
global model
model = load_model("model_keras/new_model.h5", compile=False)
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
              loss='categorical_crossentropy', metrics=['accuracy'])
# global fire_cascade
# global gun_cascade
# global knife_cascade

# # global scale
# global neigh

global thread
global cap
global userid


def get_prediction(frame):
    # Resize the frame
    img = cv2.resize(frame, dsize=(200, 200))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Preprocess the image
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)

    # Get prediction
    prediction = model.predict(img)

    return prediction


def save_image_with_unique_name(image, folder_path="output_images"):

    # Generate a unique filename using timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    file_name = f"fire_{timestamp}.jpg"
    global userid

    # Save the image with the unique filename
    cv2.imwrite(os.path.join(folder_path, file_name), image)
    try:

        query = "INSERT INTO images (images, userid) VALUES (?, ?)"
        # reading from the file

        params = (file_name, userid)
        db = DatabaseConnection()
        db.connect()
        result = db.execute_and_fetch_query(query, False, params)
        if result:
            print("Image saved successfully")
        else:
            print("Failed to save image")

    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        del db


def prediction_process(frame_queue, result_queue):
    while True:
        frame = frame_queue.get()
        prediction = get_prediction(frame)
        result_queue.put(prediction)


def create_trackbars():
    cv2.namedWindow("Track")
    cv2.moveWindow("Track", 0, 380)
    cv2.resizeWindow("Track", 600, 180)
    cv2.createTrackbar("Scale", "Track", 100, 1000, lambda x: None)
    cv2.createTrackbar("Neigh", "Track", 5, 50, lambda x: None)
    cv2.createTrackbar("Min area", "Track", 0, 100000, lambda x: None)
    cv2.createTrackbar("Brightness", "Track", 0, 255, lambda x: None)


def get_trackbar_position():

    scale = 1 + (cv2.getTrackbarPos("Scale", "Track") / 1000)
    neigh = (cv2.getTrackbarPos("Neigh", "Track")+1)
    min_area = cv2.getTrackbarPos("Min area", "Track")
    brightness = cv2.getTrackbarPos("Brightness", "Track")

    return scale, neigh, min_area, brightness


def send_notification(type: int):
    time.sleep(1)

    if type == 0:

        winsound.Beep(1000, 2 * 1000)  # 1000 Hz frequency for 2 seconds
        notification.notify(title="Fire Detected!",
                            message="An object has been detected using the Haar cascade.", app_name="Haradous_Object_DetectION")

    elif type == 1:

        winsound.Beep(1000, 2 * 1000)  # 1000 Hz frequency for 2 seconds

        notification_message = "An object has been detected using the Haar cascade."
        notification.notify(title="Gun Detected!",
                            message=notification_message, app_name="Haradous Object Detector")

    elif type == 2:

        winsound.Beep(1000, 2 * 1000)  # 1000 Hz frequency for 2 seconds
        notification_title = "Knife Detected!"
        notification_message = "An object has been detected using the Haar cascade."
        notification.notify(title=notification_title,
                            message=notification_message, app_name="Haradous Object Detector")
    else:
        pass


def capture_and_predict():
    global thread
    global cap
    global userid

    with open("userid.txt", "r") as f:
        userid = int(f.read())

    # t = threading.Thread(target=get_userid)
    # t.daemon = True
    # t.start()

    fire_cascade = cv2.CascadeClassifier("HaarCascade/fire_detection.xml")
    gun_cascade = cv2.CascadeClassifier("HaarCascade/myhaar_gun_cascade.xml")
    knife_cascade = cv2.CascadeClassifier(
        "HaarCascade/myhaar25_iteration_scale100_neigh5.xml")

    create_trackbars()

    # Open the default camera
    cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture('videos/fire/c2.mp4')
    frame_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    # Create a process for prediction
    prediction_proc = multiprocessing.Process(
        target=prediction_process, args=(frame_queue, result_queue))
    prediction_proc.daemon = True  # Terminate when the main process terminates
    prediction_proc.start()

    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()

        # If frame is read correctly ret is True

        if ret:
            frame = cv2.resize(frame, (640, 480))
            grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Put frame into the frame queue
            frame_queue.put(frame)

            # Get trackbar position
            scale, neig, min_area, brightness = get_trackbar_position()
            cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)

            # Get prediction result from the result queue
            prediction = result_queue.get()

            print(prediction[0][0])

            # Perform cascade classifier detection based on prediction
            if prediction[0][0] >= 0.5:

                # Detect fire
                fire_regions = fire_cascade.detectMultiScale(
                    frame, scaleFactor=scale, minNeighbors=neig)

                confidence = len(fire_regions)
                print(confidence, "fire Cascade")

                if len(fire_regions) > 0:
                    for (x, y, w, h) in fire_regions:
                        cv2.rectangle(frame, (x-20, y-20), (x+w+20, y+h+20),
                                      (255, 0, 0), 2)
                        cv2.putText(frame, "Fire", (x-20, y-20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

                    saving_thread = threading.Thread(
                        target=save_image_with_unique_name, args=(frame,))
                    saving_thread.daemon = True
                    saving_thread.start()

                    thread = threading.Thread(
                        target=send_notification, args=(0,))
                    thread.daemon = True
                    thread.start()
                    # send_notification(0)

                    # cv2.imshow("live Hod", frame)
                    # Send desktop notification

                    # continue

            elif prediction[0][1] >= 0.5:

                # Detect gun
                gun_regions = gun_cascade.detectMultiScale(
                    grey, scaleFactor=scale, minNeighbors=neig)
                if len(gun_regions) > 0:
                    for (x, y, w, h) in gun_regions:
                        cv2.rectangle(frame, (x-15, y-15),
                                      (x+w+15, y+h+15), (0, 255, 0), 2)
                        cv2.putText(frame, "Gun", (x-15, y-15),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            elif prediction[0][2] >= 0.9:
                # Detect knife
                knife_regions = knife_cascade.detectMultiScale(
                    frame, scaleFactor=scale, minNeighbors=neig)
                if len(knife_regions) > 0:
                    for (x, y, w, h) in knife_regions:
                        cv2.rectangle(frame, (x, y), (x+w, y+h),
                                      (0, 0, 255), 2)
                        cv2.putText(frame, "Knife", (x, y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            # Print prediction result
            print("Prediction:", prediction)

            # Print prediction result
            print("Prediction:", prediction, type(
                prediction), np.argmax(prediction))

            # Display the frame
            cv2.imshow('frame', frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Error: Failed to capture frame")
            break

    cap.release()
    cv2.destroyAllWindows()


def destroy_window():
    global cap
    cap = False
    # Release the camera and close OpenCV windows


# if __name__ == "__main__":
#     capture_and_predict()
