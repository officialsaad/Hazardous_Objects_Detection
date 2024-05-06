import cv2
import numpy as np
import threading
import os

import tensorflow as tf
from keras.models import load_model
from tkinter import messagebox
import time
import multiprocessing

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


model = load_model('model_keras/new_model.h5', compile=False)
model.compile(optimizer=tf.keras.optimizers.Adam(
), loss='categorical_crossentropy', metrics=['accuracy'])
fire_cascade = cv2.CascadeClassifier('HaarCascade/fire_detection.xml')

thread_list = {}
process_list = []

prediction_dic = {}

def draw_threaded(gray_img, scale_value, neig, img2, font, fontScale, color, thickness, min_area, cascade=None, cascade_type='fire', min_area_less=True, no_min_area=False):
    if cascade is not None:
        def draw_task():
            fires = cascade.detectMultiScale(gray_img, scale_value, neig)

            for (x, y, w, h) in fires:
                area = w * h
                org = (x - 10, y - 10)

                if no_min_area:
                    cv2.rectangle(img2, (x - 20, y - 20),
                                  (x + w + 20, y + h + 20), (255, 0, 0), 2)
                    cv2.putText(img2, cascade_type, (x - 20, y - 20), font,
                                fontScale, color, thickness, cv2.LINE_AA)
                    roi_gray = gray_img[y:y + h, x:x + w]
                    roi_color = img2[y:y + h, x:x + w]
                else:
                    if min_area_less:
                        if area < min_area:
                            cv2.rectangle(img2, (x - 20, y - 20),
                                          (x + w + 20, y + h + 20), (255, 0, 0), 2)
                            cv2.putText(img2, cascade_type, (x - 20, y - 20), font,
                                        fontScale, color, thickness, cv2.LINE_AA)
                            roi_gray = gray_img[y:y + h, x:x + w]
                            roi_color = img2[y:y + h, x:x + w]
                    else:
                        if area > min_area:
                            cv2.rectangle(img2, (x - 20, y - 20),
                                          (x + w + 20, y + h + 20), (255, 0, 0), 2)
                            cv2.putText(img2, cascade_type, (x - 20, y - 20), font,
                                        fontScale, color, thickness, cv2.LINE_AA)
                            roi_gray = gray_img[y:y + h, x:x + w]
                            roi_color = img2[y:y + h, x:x + w]

        draw_task()

        return img2

    else:
        print("No Cascade is available")
        messagebox.showerror("Error", "No Cascade Classifier is available")
        return


def get_prediction(model, img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, dsize=(200, 200))
    img = img * 1./ 255
    img = np.expand_dims(img, axis=0)
  
    prediction_dic["prediction"] = model.predict(img)

def emt(x):
    pass


def fun(frame_width=400, frame_height=480):

    capture = cv2.VideoCapture(1)
    # capture = cv2.VideoCapture(r"videos\fire\c2.mp4")

    cv2.namedWindow("Track")
    cv2.moveWindow("Track", 0, 380)
    cv2.resizeWindow("Track", 600, 180)
    cv2.createTrackbar("Scale", "Track", 100, 1000, emt)
    cv2.createTrackbar("Neigh", "Track", 5, 50, emt)
    cv2.createTrackbar("Min area", "Track", 0, 100000, emt)
    cv2.createTrackbar("Brightness", "Track", 0, 255, emt)

    img_count_full = 0

    # parameters for text
    # font
    font = cv2.FONT_HERSHEY_SIMPLEX
    # origin
    org = (1, 1)
    class_lable = ' '
    # fontScale
    fontScale = 1  # 0.5
    # Blue color in BGR
    color = (255, 0, 0)
    # Line thickness of 2 px
    thickness = 1  # 1

    while capture.isOpened():
        ret, frame = capture.read()

        
        # self.get_prediction(self.model, img=frame)

        prediction_thread = threading.Thread(target=get_prediction, args=(model, frame))
        prediction_thread.start()

        
        
        # process_list.append(p)

        
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # self.get_prediction(self.model, frame)

        if ret == True:

            bright = cv2.getTrackbarPos("Brightness", "Track")
            capture.set(10, bright)
            img2 = cv2.resize(frame, (frame_width, frame_height))
            gray_img = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

            scale_value = 1 + (cv2.getTrackbarPos("Scale", "Track") / 1000)
            neig = (cv2.getTrackbarPos("Neigh", "Track") + 1)
            img_count_full += 1

            # for _ in process_list:
            #     if _ == p: 
            #         if _.is_alive():
            #             _.join()      
            #         else:
            #             process_list.remove(_)

            if prediction_thread.is_alive():
                prediction_thread.join()
            else:
                print("Thread is dead")    

            prediction = prediction_dic.get("prediction")

            if prediction is None:
                continue
            else:
                print(prediction)

                if prediction[0][0] >= 0.5:

                    # self.draw_threaded(gray_img=gray_img,scale_value=scale_value,neig=neig,img2=img2,font=font,fontScale=fontScale,color=color,thickness=thickness,min_area=cv2.getTrackbarPos("Min area", "Track"),cascade=self.fire_cascade,min_area_less=True, no_min_area=False)
                    # # min_area_less = True means if area is less than min_area then draw rectangle and text
                    # # no_min_area = False means if area is avilable then check for less or greater area then draw rectangle and text
                    img2 = draw_threaded(gray_img=gray_img, scale_value=scale_value, neig=neig, img2=img2, font=font, fontScale=fontScale, color=color, thickness=thickness,
                                         min_area=cv2.getTrackbarPos("Min area", "Track"), cascade=fire_cascade, cascade_type='fire', min_area_less=False, no_min_area=False)
            # self.draw_threaded(gray_img=gray_img,scale_value=scale_value,neig=neig,img2=img2,font=font,fontScale=fontScale,color=(255,255,0),thickness=thickness,min_area=cv2.getTrackbarPos("Min area", "Track"),cascade=self.gun_cascade, cascade_type='Gun',min_area_less=True, no_min_area=False)

                    cv2.imshow("Live HOD Detection System",
                               img2)

                elif prediction[0][1] >= 0.65:
                    pass

                elif prediction[0][2] >= 0.65:
                    pass

                else:
                    cv2.imshow("Live HOD Detection System", img2)

            if cv2.waitKey(1) & 0xff == ord('q'):
                break

        else:
            break

    capture.release()
    cv2.destroyAllWindows()


def main_function():
    try:
        fun(frame_width=640, frame_height=480)
    except Exception as e:
        messagebox.showerror("Video Turned off", f"Error: {e}")


if __name__ == "__main__":
    # p = multiprocessing.Process(target=main_function)
    # p.start()
    # p.join()
    main_function()
