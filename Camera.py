import multiprocessing.process
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


class Camera:
    def draw_threaded(self, gray_img, scale_value, neig, img2, font, fontScale, color, thickness, min_area, cascade=None, cascade_type: str = 'fire' or 'gun' or 'knife', min_area_less=True, no_min_area=False):
        # Define the function to be executed in a thread
        if cascade is None:
            print("No Cascade is aviable")
            messagebox.showerror("Error", "No Cascade Cassifier is aviable")
            return
        else:
            def draw_task():
                fires = cascade.detectMultiScale(gray_img, scale_value, neig)

                print("fire Value :", fires)

                for (x, y, w, h) in fires:
                    area = w * h
                    org = (x - 10, y - 10)

                    if no_min_area:
                        with self.result_lock:
                            cv2.rectangle(img2, (x - 20, y - 20),
                                          (x + w + 20, y + h + 20), (255, 0, 0), 2)
                            cv2.putText(img2, cascade_type, (x - 20, y - 20), font,
                                        fontScale, color, thickness, cv2.LINE_AA)
                            roi_gray = gray_img[y:y + h, x:x + w]
                            roi_color = img2[y:y + h, x:x + w]
                    else:
                        if min_area_less:
                            if area < min_area:
                                with self.result_lock:
                                    cv2.rectangle(img2, (x - 20, y - 20),
                                                  (x + w + 20, y + h + 20), (255, 0, 0), 2)
                                    cv2.putText(img2, cascade_type, (x - 20, y - 20), font,
                                                fontScale, color, thickness, cv2.LINE_AA)
                                    roi_gray = gray_img[y:y + h, x:x + w]
                                    roi_color = img2[y:y + h, x:x + w]
                            else:
                                pass

                        else:
                            if area > min_area:
                                with self.result_lock:
                                    cv2.rectangle(img2, (x - 20, y - 20),
                                                  (x + w + 20, y + h + 20), (255, 0, 0), 2)
                                    cv2.putText(img2, cascade_type, (x - 20, y - 20), font,
                                                fontScale, color, thickness, cv2.LINE_AA)
                                    roi_gray = gray_img[y:y + h, x:x + w]
                                    roi_color = img2[y:y + h, x:x + w]

            # Create and start the thread
            thread = threading.Thread(target=draw_task)
            thread.start()
            # Wait for the thread to finish
            thread.join()

            # Update the img2 attribute with the modified image
            with self.result_lock:
                self.result_img = img2

    def __init__(self):
        self.frame_width = 600
        self.frame_height = 400
        self.gun_cascade = cv2.CascadeClassifier(
            "HaarCascade/myhaar_gun_cascade.xml")
        self.fire_cascade = cv2.CascadeClassifier(
            "HaarCascade/fire_detection.xml")
        self.knife_cascade = cv2.CascadeClassifier(
            "HaarCascade/myhaar25_iteration_scale100_neigh5.xml")

        self.result_lock = threading.Lock()
        self.result_img = None

        model_path = "model_keras/new_model.h5"

        self.model = load_model(model_path, compile=False)
        self.model.compile(optimizer=tf.keras.optimizers.Adam(
        ), loss='categorical_crossentropy', metrics=['accuracy'])

        self.prediction = None

        self.processes_list = []

    def emt(self, x):
        pass

    def turn_on_carmera(self):
        self.cap = cv2.VideoCapture('videos/fire/c2.mp4')
        while self.cap.isOpened():
            self.ret, self.frame = self.cap.read()
            print("camera opend")

            if self.ret == True:

                trackbar_thread = threading.Thread(
                    target=self.get_control_value)
                trackbar_thread.start()
                # not use the join here because it will continue

                # prediction_thread = threading.Thread(target=self.get_prediction, args=(self.model, self.frame))
                # prediction_thread.start()
                # prediction_thread.join()

                convert_thread = threading.Thread(
                    target=self.convert_img, args=(self.frame,))
                convert_thread.start()
                convert_thread.join()

                cor = self.fire_cascade.detectMultiScale(
                    self.grey_image, self.scale_value, self.neig)

                for (x, y, w, h) in cor:
                    area = w * h
                    org = (x - 15, y - 15)
                    # img_count += 1

                    # color_face = color_img[y:y + h, x:x + w]
                    if area < self.min_area:
                        cv2.rectangle(self.resized_img, org,
                                      (x + w + 15, y + h + 15), (255, 0, 0), 2)
                        roi_gray = self.grey_image[y:y + h+25, x:x + w+25]
                        roi_color = self.rgb_image[y:y + h+30, x:x + w+30]
                        # roi_color = cv2.resize(roi_color, dsize=(200, 200))
                        # roi_color = cv2.cvtColor(roi_color, cv2.COLOR_BGR2RGB)
                        cv2.putText(self.resized_img, "fire", org, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(
                                    0, 255, 0), thickness=1, lineType=cv2.LINE_AA)

                cv2.imshow("LiVE HOD Detection", self.resized_img)

                # self.draw_rectangle(self.fire_cascade)

                # if self.prediction is not None:
                #     # print(self.prediction)
                #     self.draw_rectangle()
                #     # trackbar_thread.join()

                # else:
                #     print("Prediction is none")

                # cv2.imshow("LiVE HOD Detection", self.resized_img)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                else:
                    pass

                # show img

            else:
                messagebox.showerror('Image Capture Error',
                                     'Camera is not open')

    def turn_off_camera(self):
        cv2.release()
        cv2.destroyAllWindows()

    def get_control_value(self):

        self.brightness = cv2.getTrackbarPos("Brightness", "Track")
        self.cap.set(10, self.brightness)
        self.scale_value = max(
            1 + (cv2.getTrackbarPos("Scale", "Track") / 1000), 1.1)
        self.neig = (cv2.getTrackbarPos("Neigh", "Track") + 1)
        self.min_area = (cv2.getTrackbarPos("Min area", "Track"))

    # def convert_img(self, img, frame_width=640, frame_height=480):
    #     self.resized_img = cv2.resize(img, dsize=(
    #         frame_width, frame_height))
    #     self.grey_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #     self.rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def get_prediction(self, model, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, dsize=(200, 200))
        img = img.astype(np.float64) / 255.0
        img = np.expand_dims(img, axis=0)
        self.prediction = model.predict(img)

    # def detect_haar_cascades(self, gray_img):
    #     # Detect objects using Haar cascades
    #     fire_regions = self.fire_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    #     gun_regions = self.gun_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    #     knife_regions = self.knife_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    #     return fire_regions, gun_regions, knife_regions

    # def draw(self, gray_img, scale_value, neig, img2 , font, fontScale, color, thickness,min_area):

    #     fires = self.fire_cascade.detectMultiScale(
    #                 gray_img, scale_value, neig)

    #     img_count = 0
    #     for (x, y, w, h) in fires:
    #         area = w * h
    #         min_area = (cv2.getTrackbarPos("Min area", "Track"))
    #         org = (x - 10, y - 10)
    #         img_count += 1

    #     # color_face = color_img[y:y + h, x:x + w]

    #         if area > min_area:
    #             cv2.rectangle(img2, (x - 20, y - 20),
    #                             (x + w + 20, y + h + 20), (255, 0, 0), 2)
    #             roi_gray = gray_img[y:y + h, x:x + w]
    #             roi_color = img2[y:y + h, x:x + w]
    #             cv2.putText(img2, "fire", (x - 20, y - 20), font,
    #                         fontScale, color, thickness, cv2.LINE_AA)

    # # # take face then predict class mask or not mask then draw recrangle and text then display image
    #     img_count = 0
    #     cv2.imshow("Live HOD Detection System", img2)

    def __del__(self):
        pass

    def fun(self):
        frame_width = self.frame_width
        frame_height = self.frame_height
        capture = cv2.VideoCapture(1)
        # capture = cv2.VideoCapture(r"videos\fire\c2.mp4")

        cv2.namedWindow("Track")
        cv2.moveWindow("Track", 0, 380)
        cv2.resizeWindow("Track", 600, 180)
        cv2.createTrackbar("Scale", "Track", 100, 1000, self.emt)
        cv2.createTrackbar("Neigh", "Track", 5, 50, self.emt)
        cv2.createTrackbar("Min area", "Track", 0, 100000, self.emt)
        cv2.createTrackbar("Brightness", "Track", 0, 255, self.emt)

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

            process = threading.Thread(
                target=self.get_prediction, args=(self.model, frame))
            process.start()
            self.processes_list.append(process)
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

                for _ in self.processes_list:
                    if not _.is_alive():
                        self.processes_list.remove(_)
                    else:
                        _.join()

                if self.prediction is None:
                    pass
                else:
                    print(self.prediction)

                    if self.prediction[0][0] >= 0.5:

                        # self.draw_threaded(gray_img=gray_img,scale_value=scale_value,neig=neig,img2=img2,font=font,fontScale=fontScale,color=color,thickness=thickness,min_area=cv2.getTrackbarPos("Min area", "Track"),cascade=self.fire_cascade,min_area_less=True, no_min_area=False)
                        # # min_area_less = True means if area is less than min_area then draw rectangle and text
                        # # no_min_area = False means if area is avilable then check for less or greater area then draw rectangle and text
                        self.draw_threaded(gray_img=gray_img, scale_value=scale_value, neig=neig, img2=img2, font=font, fontScale=fontScale, color=color, thickness=thickness,
                                           min_area=cv2.getTrackbarPos("Min area", "Track"), cascade=self.fire_cascade, cascade_type='fire', min_area_less=False, no_min_area=False)
                        with self.result_lock:
                            cv2.imshow("Live HOD Detection System", self.result_img)
                # self.draw_threaded(gray_img=gray_img,scale_value=scale_value,neig=neig,img2=img2,font=font,fontScale=fontScale,color=(255,255,0),thickness=thickness,min_area=cv2.getTrackbarPos("Min area", "Track"),cascade=self.gun_cascade, cascade_type='Gun',min_area_less=True, no_min_area=False)

                        # cv2.imshow("Live HOD Detection System",
                        #            self.result_img)

                    elif self.prediction[0][1] >= 0.65:
                        self.draw_threaded(gray_img=gray_img, scale_value=scale_value, neig=neig, img2=img2, font=font, fontScale=fontScale, color=(155, 0, 255), thickness=thickness,
                                           min_area=cv2.getTrackbarPos("Min area", "Track"), cascade=self.gun_cascade, cascade_type='gun', min_area_less=False, no_min_area=False)
                        with self.result_lock:
                            cv2.imshow("Live HOD Detection System", self.result_img)

                    elif self.prediction[0][2] >= 0.5:
                        self.draw_threaded(gray_img=gray_img, scale_value=scale_value, neig=neig, img2=img2, font=font, fontScale=fontScale, color=(155, 155, 3), thickness=thickness,
                                           min_area=cv2.getTrackbarPos("Min area", "Track"), cascade=self.knife_cascade, cascade_type='Knife', min_area_less=False, no_min_area=False)
                        with self.result_lock:
                            cv2.imshow("Live HOD Detection System", self.result_img)

                    else:
                        cv2.imshow("Live HOD Detection System", img2)

                

                if cv2.waitKey(1) & 0xff == ord('q'):
                    break

            else:
                messagebox.showerror("Captur Image", "Failed to Capture Image")
                break

        capture.release()
        cv2.destroyAllWindows()


def main_function():
    try:
        cam = Camera()
        cam.fun()

    except Exception as e:
        messagebox.showerror("Video Turned off", f"Error: {e}")


if __name__ == "__main__":
    list_processes = []
    p = multiprocessing.Process(target=main_function)
    p.start()

    list_processes.append(p)

    for _ in list_processes:
        _.join()
