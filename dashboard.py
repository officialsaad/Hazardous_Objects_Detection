import re
import sqlite3
from itertools import chain
from tkinter import messagebox

import PIL.Image
import customtkinter as ctk
from PIL import Image, ImageTk
from customtkinter import *

# import cv2
from Camera import Camera
from database_connection import DatabaseConnection
from multi import *


class admin:
    __password: str
    __answer: str
    __contact: str
    __ques: str
    __id: int
    __name = str
    __email = str

    def __init__(self):
        self.__id = 0
        self.__name = ""
        self.__contact = ""
        self.__email = ""
        self.__ques = ""
        self.__answer = ""
        self.__password = ""

    def setid(self, id):

        if id != "" and id != 0:
            self.__id = id
        else:
            messagebox.showerror("Id Contain String", "Id can not be alphabet")

    def setname(self, name):
        if name == "":
            messagebox.showerror("Empty Name", "Name cannot be Empty")
        else:
            result = all(char.isalpha() or char.isspace() for char in name)
            if result and name.strip():  # Check if all characters are alphabets or spaces, and the name is not empty after stripping spaces
                self.__name = name
            else:
                messagebox.showerror("Invalid Name",
                                     "Name should contain only alphabets and spaces, and cannot be empty")

    def setcontact(self, c):
        if c == "":
            messagebox.showerror("Empty Contact", "Contact cannot be null")
        else:
            if not c.isdigit():
                messagebox.showerror(
                    "Invalid Contact", "Contact should contain only digits")
            else:
                self.__contact = c

    def setemail(self, email):
        if email == "":
            messagebox.showerror("Empty Email", "Email cannot be null")
        else:
            # Basic email format validation using a regular expression
            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if re.match(email_pattern, email):
                self.__email = email
            else:
                messagebox.showerror(
                    "Invalid Email", "Please enter a valid email address")

    def setquest(self, ques):
        if ques == "":
            messagebox.showerror("Empty Question", "Question cannot be null")
        elif ques == "select":
            messagebox.showerror("Empty Question", "Please choose question")
        else:
            if not all(char.isalpha() or char.isspace() for char in ques):
                messagebox.showerror(
                    "Invalid Characters", "Question should contain only alphabets and spaces")
            else:
                self.__ques = ques

    def setanswer(self, answer):
        if answer == "":
            messagebox.showerror("Empty Answer", "Answer cannot be null")
        elif len(answer) > 30:
            messagebox.showerror(
                "Invalid Length", "Answer should be at most 30 characters")
        elif not all(char.isalpha() or char.isspace() for char in answer):
            messagebox.showerror(
                "Invalid Characters", "Answer should contain only alphabets and spaces")
        else:
            self.__answer = answer

    def setpassword(self, password):
        if password == "":
            messagebox.showerror("Empty Password", "Password cannot be null")
        elif len(password) < 8:
            messagebox.showerror(
                "Invalid Length", "Password should be at least 8 characters")
        else:
            self.__password = password

    def getid(self):
        return self.__id

    def getname(self):
        return self.__name

    def getemail(self):
        return self.__email

    def getpassword(self):
        return self.__password

    def getcontact(self):
        return self.__contact

    def getquestion(self):
        return self.__ques

    def getanswer(self):
        return self.__answer

    def insert(self):
        query = 'select * from registration where email = ?'
        param = (self.__email,)
        # check if email already exist
        if param[0] == "":
            return False
        else:
            db = DatabaseConnection()
            db.connect()
            result = db.execute_and_fetch_query(query, True, param)
            del db
        if result:
            messagebox.showerror(
                "Email Exist", "Email already exist, please use another email")
            return False
        else:
            query = 'INSERT INTO registration (name, contact_no, email, question, answer, password) VALUES (?,?,?,?,?,?)'
            param = (self.__name, self.__contact, self.__email,
                     self.__ques, self.__answer, self.__password)
            for _ in param:
                if _ == "":
                    messagebox.showerror(
                        "Empty Value Error", "Please Fill All Fields")
                    return False
                else:
                    db = DatabaseConnection()
                    db.connect()
                    result = db.execute_and_fetch_query(query, False, param)
                    del db
                    return result

    def read(self):
        query = 'select * from registration where id = ?'
        param = (self.__id,)
        db = DatabaseConnection()
        db.connect()
        result = db.execute_and_fetch_query(query, True, param)
        del db
        return result

    # def update(self):
    #     query = 'update registration set name = ?, contact_no = ?, email = ?, question = ?, answer = ?, password = ? where id = ?'
    #     #
    #     param = (self.__name, self.__contact, self.__email, self.__ques, self.__answer, self.__password, self.__id)
    #     db = DatabaseConnection()
    #     db.connect()
    #     result = db.execute_and_fetch_query(query, True, param)
    #     return result

    def update(self):

        query = 'UPDATE registration SET name = ?, contact_no = ?, email = ?, question = ?, answer = ?, password = ? WHERE id = ?'
        params = (self.__name, self.__contact, self.__email,
                  self.__ques, self.__answer, self.__password, self.__id)

        for _ in params:
            if _ == "":
                messagebox.showerror(
                    "Empty Value Error", "Please Fill All Fields")
                return False
            else:
                db = DatabaseConnection()
                db.connect()
                try:
                    db.execute_and_fetch_query(query, False, params)
                    # db.commit()  # Commit changes for UPDATE query
                    return True
                except sqlite3.Error as e:
                    print(f"Error in update query: {e}")
                    db.rollback()  # Rollback changes in case of an error
                    messagebox.showerror("Error", str(e))
                finally:
                    del db

    def delete(self):
        query = 'delete from registration where id = ?'
        param = (self.__id,)
        db = DatabaseConnection()
        db.connect()
        result = db.execute_and_fetch_query(query, False, param)
        del db
        return True

    def __del__(self):
        del self.__id
        del self.__name
        del self.__email
        del self.__ques
        del self.__password
        del self.__answer


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


class dashboard:
    def __init__(self, root, user=1):

        self.process_list = []
        self.p = None

        # for user
        self.__userid = user
        self.__userdata = []

        # for styling
        # self.btn_list = []
        # self.label_list = []

        self.theme_color_default = "blue"
        self.hover_color = ("#09BB98", "#09BB98")
        self.fg_color = ("purple", "black")
        # self.fg_color = None
        self.font = ("times new roman", 16)
        self.text_color = "white"
        self.frame_color = ("black", "white")

        # for the app
        self.root = root
        self.root.geometry("1200x660+100+20")

        # for frames
        self.create_left_frame()
        self.create_log_frame()
        self.create_right_frame()
        self.user_data()

    def create_log_frame(self):

        self.left_frame.destroy()

        self.left_frame = ctk.CTkFrame(
            self.root, fg_color="#D4CDCE", corner_radius=10)
        self.left_frame.pack(side="left", fill="y",
                             padx=(20, 10), pady=(15, 15))

        logo = ctk.CTkLabel(self.left_frame, fg_color="#181818", text_color="white", width=225, height=130,
                            text="HOD Dashboard", font=("times new roman", 20), corner_radius=30)
        logo.pack(anchor="nw", padx=(10, 10), pady=(10, 10))

        sframe = ctk.CTkScrollableFrame(
            self.left_frame, width=200, height=600, fg_color="white")
        sframe.pack(side="left", padx=(10, 10), pady=(5, 20))

        reg_btn = ctk.CTkButton(sframe, text="Registration", font=self.font, text_color=self.text_color,
                                hover_color=self.hover_color, fg_color=self.fg_color, command=self.register_data,
                                border_width=1, corner_radius=30, height=40)
        reg_btn.pack(fill="x", pady=(0, 15), padx=(10, 10))

        login = ctk.CTkButton(sframe, text="Log in", font=self.font, text_color=self.text_color,
                              hover_color=self.hover_color, fg_color=self.fg_color, command=self.login_fun,
                              border_width=1, corner_radius=30, height=40)
        login.pack(fill="x", pady=(0, 15), padx=(10, 10))

        exit = ctk.CTkButton(sframe, text="Exit", font=self.font, text_color=self.text_color,
                             hover_color=self.hover_color, fg_color=self.fg_color, command=self.exit_fun,
                             border_width=1, corner_radius=30, height=40)
        exit.pack(fill="x", pady=(0, 15), padx=(10, 10))

    def exit_fun(self):
        self.root.destroy()

    def login_fun(self):
        self.frame2.destroy()
        self.create_right_frame()

        img2 = ctk.CTkImage(light_image=PIL.Image.open("images/sk.jpg"), dark_image=PIL.Image.open("images/sk.jpg"),
                            size=(1366, 768))
        # img1 = ImageTk.PhotoImage(PIL.Image.open("images/sk.jpg"))

        img_label = CTkLabel(master=self.frame2, image=img2)
        img_label.pack()

        frame = ctk.CTkFrame(
            master=self.frame2, width=300, height=400)
        frame.place(relx=0.5, rely=0.5, anchor='center')

        sign_label = ctk.CTkLabel(
            frame, text="Sign in", bg_color="transparent", width=200)
        sign_label.place(relx=0.5, rely=0.1, anchor='center')

        self.username = ctk.CTkEntry(frame, font=(
            "times new roman", 12), width=220, height=25, bg_color="transparent", corner_radius=0,
            placeholder_text="Enter Your Email")
        # self.username.place(x=300, y=160)
        self.username.place(relx=0.5, rely=0.25, anchor='center')

        self.password = ctk.CTkEntry(frame, font=(
            "times new roman", 12), width=220, height=25, bg_color="transparent", corner_radius=0, show="*",
            placeholder_text="Enter Your Password")
        self.password.place(relx=0.5, rely=0.35, anchor='center')

        self.btn_show_password = ctk.CTkButton(
            frame, text="Show Password", width=220, height=30, fg_color=self.fg_color, hover_color=self.hover_color,
            corner_radius=0, command=self.toggle_password)
        self.btn_show_password.place(rely=0.5, relx=0.5, anchor='center')

        self.btn = ctk.CTkButton(frame, text="Log in", width=220,
                                 height=30, corner_radius=0, fg_color=self.fg_color, hover_color=self.hover_color,
                                 command=self.login_fun2)
        self.btn = self.btn.place(relx=0.5, rely=0.6, anchor='center')

        self.forget_btn = ctk.CTkButton(frame, text="Forget Password",
                                        width=220, fg_color=self.fg_color, hover_color=self.hover_color, height=30,
                                        corner_radius=0, command=self.forget_pass_form)
        self.forget_btn = self.forget_btn.place(
            relx=0.5, rely=0.7, anchor='center')

        self.reg_btn = ctk.CTkButton(frame, text="Registration",
                                     width=220, height=30, fg_color=self.fg_color, hover_color=self.hover_color,
                                     corner_radius=0, command=self.regwindow)
        self.reg_btn = self.reg_btn.place(relx=0.5, rely=0.8, anchor='center')

    def toggle_password(self):
        current_show_value = self.password.cget("show")
        if current_show_value == "*":
            self.password.configure(show="")
            self.btn_show_password.configure(text="Hide Password")
        else:
            self.password.configure(show="*")
            self.btn_show_password.configure(text="Show Password")

    def forget_pass_form(self):
        self.frame2.destroy()
        self.create_right_frame()

        frame1 = ctk.CTkFrame(
            master=self.frame2, border_color="black", width=300, height=400)
        frame1.place(relx=0.5, rely=0.5, anchor='center')

        self.sign_label = ctk.CTkLabel(
            frame1, text="Forget Password", bg_color="transparent", width=220)
        self.sign_label.place(relx=0.5, rely=0.1, anchor='center')

        self.txt_email = ctk.CTkEntry(frame1, font=(
            "times new roman", 12), width=220, height=25, corner_radius=0, placeholder_text="Enter Your Email")
        self.txt_email.place(relx=0.5, rely=0.25, anchor='center')

        self.cmb_ques = ctk.CTkComboBox(master=frame1,
                                        values=[
                                            "Your First Pet Name", "Your Birth Place", "Your Best Friend Name"],
                                        dropdown_hover_color=self.hover_color,
                                        width=220, height=25, corner_radius=0, state="readonly")
        self.cmb_ques.set("Select")
        self.cmb_ques.place(relx=0.5, rely=0.35, anchor='center')

        self.txt_answer = ctk.CTkEntry(master=frame1, font=(
            "times new roman", 12), width=220, height=25, corner_radius=0, placeholder_text="Enter Your Answer")
        self.txt_answer.place(relx=0.5, rely=0.45, anchor='center')

        self.verify = ctk.CTkButton(master=frame1, text="Verify", corner_radius=0,
                                    fg_color=self.fg_color, hover_color=self.hover_color,
                                    command=self.verification_password, width=220, height=30)
        self.verify.place(rely=0.6, relx=0.5, anchor='center', )

        self.login = ctk.CTkButton(master=frame1, text="Back to Log in", corner_radius=0,
                                   fg_color=self.fg_color, hover_color=self.hover_color,
                                   command=self.login_fun, width=220, height=30)
        self.login.place(rely=0.7, relx=0.5, anchor='center')

    def verification_password(self):
        email = self.txt_email.get().lower()
        ques = self.cmb_ques.get().lower()
        answer = self.txt_answer.get().lower()
        if ques == "select":
            messagebox.showinfo("Security Question Not Selected",
                                "Please Choose the Security Question ")
        else:
            if email == "":
                messagebox.showinfo("Email Empty", "Please Enter Your email ")
            elif answer == "":
                messagebox.showinfo("Answer Empty", "Please Enter Your Answer")
            elif ques == "select":
                messagebox.showinfo("Select Box Empty",
                                    "Please Select your Question")
            else:
                # Using parameterized query
                query = 'SELECT id FROM registration WHERE email = ? AND question = ? AND answer = ?'
                # param = (email,ques,answer)
                db = DatabaseConnection()
                db.connect()
                result = db.execute_and_fetch_query(
                    query, True, (email, ques, answer))
                if result:
                    self.user_id = result[0][0]
                    print(self.user_id)
                    messagebox.showinfo("Verification", "Sucessfully Verified")

                    self.frame2.destroy()
                    self.create_right_frame()

                    self.new_pass_frame()

                else:
                    messagebox.showerror("Wrong Input", result)

                del db

    def new_pass_frame(self):

        frame = ctk.CTkFrame(
            master=self.frame2, bg_color="transparent", width=300, height=400)
        frame.place(relx=0.5, rely=0.5, anchor='center')

        self.for_label = ctk.CTkLabel(
            frame, text="Forget Password", bg_color="transparent", width=220)
        self.for_label.place(relx=0.5, rely=0.1, anchor='center')

        self.passwordi = ctk.CTkEntry(frame, font=(
            "times new roman", 12), width=220, height=25, bg_color="transparent", corner_radius=0, show="*",
            placeholder_text="Enter Your Password")
        self.passwordi.place(relx=0.5, rely=0.25, anchor='center')

        self.cpassword = ctk.CTkEntry(frame, font=(
            "times new roman", 12), width=220, height=25, bg_color="transparent", corner_radius=0, show="*",
            placeholder_text="Enter Your Password")
        self.cpassword.place(relx=0.5, rely=0.35, anchor='center')

        self.show_pass = ctk.CTkButton(frame, text="Show Password", corner_radius=0,
                                       fg_color=self.fg_color, hover_color=self.hover_color,
                                       command=self.two_pass, width=220, height=30)
        self.show_pass.place(rely=0.55, relx=0.5, anchor='center')

        self.verify = ctk.CTkButton(frame, text="Update Password", corner_radius=0,
                                    fg_color=self.fg_color, hover_color=self.hover_color,
                                    command=self.updatepass, width=220, height=30)
        self.verify.place(rely=0.65, relx=0.5, anchor='center')

        self.login = ctk.CTkButton(frame, text="Back to Log in", corner_radius=0,
                                   fg_color=self.fg_color, hover_color=self.hover_color,
                                   command=self.login_fun, width=220, height=30)
        self.login.place(rely=0.75, relx=0.5, anchor='center')

    def updatepass(self):
        password = self.passwordi.get()
        cpassword = self.cpassword.get()

        if password != cpassword and len(password) != len(cpassword):
            messagebox.showerror("Error", "Password MisMatch")
        else:
            if self.user_id == None:
                messagebox.showerror("Error", "User not found")
            else:
                query = 'update registration set password = ? where id = ?'
                db = DatabaseConnection()
                db.connect()
                result = db.execute_and_fetch_query(
                    query, False, (password, self.user_id))
                if result:
                    messagebox.showinfo("Password Changed",
                                        "Password Sucessfully updated")
                    self.destroy_frame(self.new_pass_frame)
                    self.frame = self.creating_frame()
                    self.login_frame(self.frame)
                else:
                    messagebox.showinfo("Message", result)

    def two_pass(self):
        current_show_value = self.passwordi.cget("show")
        current_show_values = self.cpassword.cget("show")
        if current_show_value == "*" and current_show_values == "*":
            self.passwordi.configure(show="")
            self.cpassword.configure(show="")
            self.show_pass.configure(text="Hide Password")
        else:
            self.passwordi.configure(show="*")
            self.cpassword.configure(show="*")
            self.show_pass.configure(text="Show Password")

    def regwindow(self):
        self.frame2.destroy()
        self.create_right_frame()
        self.register_data()

    def login_fun2(self):
        if self.username.get() == "" or self.password.get() == "":
            messagebox.showerror("Empty Field Error", "All fields are requird")
        else:
            username = self.username.get()
            password = self.password.get()
            if len(username) > 30 or len(password) > 15:
                messagebox.showerror(
                    "Error", "Enter Email in 30 characters and Password with in 15 characters, ")
            else:
                query = 'select * from registration where email = ? and password = ?'
                param = (username, password)
                db = DatabaseConnection()
                db.connect()
                result = db.execute_and_fetch_query(query, True, param)

                if result:
                    self.__userid = result[0][0]
                    with open("userid.txt", "w") as f:
                        f.write(str(self.__userid))
                    self.user_data()
                    messagebox.showinfo("Login", "Successful Login")
                    self.left_frame.destroy()
                    self.frame2.destroy()
                    self.create_left_frame()
                    self.create_right_frame()

                else:
                    messagebox.showerror(
                        "Wrong Input", result)

                del db

    def create_right_frame(self):
        self.frame2 = ctk.CTkFrame(
            self.root, fg_color="#B3B6B7", width=200, height=400, corner_radius=10)
        self.frame2.pack(side="left", expand="true",
                         fill="both", padx=(0, 20), pady=(15, 15))

    def create_left_frame(self):
        self.left_frame = ctk.CTkFrame(
            self.root, fg_color="#B3B6B7", corner_radius=10)
        self.left_frame.pack(side="left", fill="y",
                             padx=(20, 10), pady=(15, 15))

        logo = ctk.CTkLabel(self.left_frame, fg_color="#181818", text_color="white", width=225, height=130,
                            text="HOD Dashboard", font=("times new roman", 20), corner_radius=30)
        logo.pack(anchor="nw", padx=(10, 10), pady=(10, 10))

        sframe = ctk.CTkScrollableFrame(
            self.left_frame, width=200, height=600, fg_color="white")
        sframe.pack(side="left", padx=(10, 10), pady=(5, 20))

        self.home_btn = ctk.CTkButton(sframe, text="Home", font=self.font, text_color=self.text_color,
                                      hover_color=self.hover_color, fg_color=self.fg_color,
                                      command=self.create_home_frame,
                                      border_width=1, corner_radius=30, height=40)
        self.home_btn.pack(fill="x", pady=(10, 15), padx=(10, 10))

        self.update_user_profile = ctk.CTkButton(sframe, text="Update Profile", font=self.font,
                                                 text_color=self.text_color, hover_color=self.hover_color,
                                                 fg_color=self.fg_color, command=self.show_updation_data_frame,
                                                 border_width=1, corner_radius=30, height=40)
        self.update_user_profile.pack(fill="x", pady=(0, 15), padx=(10, 10))

        # self.delete_profile = ctk.CTkButton(sframe, text="Delete Profile", font=self.font, text_color=self.text_color,
        #                                     hover_color=self.hover_color, fg_color=self.fg_color,
        #                                     command=self.show_delete_data_frame,
        #                                     border_width=1, corner_radius=30, height=40)
        # self.delete_profile.pack(fill="x", pady=(0, 15), padx=(10, 10))

        self.images = ctk.CTkButton(sframe, text="Image", font=self.font, text_color=self.text_color,
                                    hover_color=self.hover_color, fg_color=self.fg_color,
                                    command=self.show_images_on_dash,
                                    border_width=1, corner_radius=30, height=40)
        self.images.pack(fill="x", pady=(0, 15), padx=(10, 10))

        self.oncamera = ctk.CTkButton(sframe, text="Turn on camera", font=self.font, text_color=self.text_color,
                                      hover_color=self.hover_color, fg_color=self.fg_color, command=self.turn_camera_on,
                                      border_width=1, corner_radius=30, height=40)
        self.oncamera.pack(fill="x", pady=(0, 15), padx=(10, 10))

        self.offcamera = ctk.CTkButton(sframe, text="Turn off camera", font=self.font, text_color=self.text_color,
                                       hover_color=self.hover_color, fg_color=self.fg_color,
                                       command=self.turn_camera_off,
                                       border_width=1, corner_radius=30, height=40)
        self.offcamera.pack(fill="x", pady=(0, 15), padx=(10, 10))

        self.theme = ctk.CTkButton(sframe, text="Theme", font=self.font, text_color=self.text_color,
                                   hover_color=self.hover_color, fg_color=self.fg_color, command=self.theme_mode,
                                   border_width=1, corner_radius=30, height=40)
        self.theme.pack(fill="x", pady=(0, 15), padx=(10, 10))

        self.logout = ctk.CTkButton(sframe, text="Logout", font=self.font, text_color=self.text_color,
                                    hover_color=self.hover_color, fg_color=self.fg_color, command=self.logout_fun,
                                    border_width=1, corner_radius=30, height=40)
        self.logout.pack(fill="x", pady=(0, 15), padx=(10, 10))

    def create_home_frame(self):
        self.frame2.destroy()
        self.create_right_frame()
        img2 = ctk.CTkImage(light_image=PIL.Image.open("images/sk.jpg"), dark_image=PIL.Image.open("images/sk.jpg"),
                            size=(1366, 768))
        # img1 = ImageTk.PhotoImage(PIL.Image.open("images/sk.jpg"))

        img_label = CTkLabel(master=self.frame2, image=img2)
        img_label.pack()

    def show_updation_data_frame(self):

        self.frame2.destroy()
        self.create_right_frame()
        self.show_updation_data_frame2()
        # self.update_profile(self.frame2)

    def show_delete_data_frame(self):
        self.frame2.destroy()
        self.create_right_frame()
        self.show_updation_data_frame2()
        self.logo_profile.configure(text="Delete Profile")
        self.btn.configure(text="Delete", command=self.delete_profile_user)
        # self.update_profile(self.frame2)

    def delete_profile_user(self):
        pass

    def turn_camera_on(self):

        # import multi
        # import multiprocessing
        # if self.p is not None:
        #     messagebox.showinfo("Message", "Camera is already on")
        #     return
        # else:
        #     self.p = multiprocessing.Process(target=capture_and_predict)
        #     self.p.daemon = True

        #     # self.process_list.append(p)
        #     self.p.start()
        if len(self.process_list) == 0:

            self.p = multiprocessing.Process(target=capture_and_predict)
            self.p.start()
            self.process_list.append(self.p)
        else:
            messagebox.showinfo("Message", "Camera is already on")
            return

        # cam = Camera()
        # cam.turn_on_carmera()

    def turn_camera_off(self):

        if len(self.process_list) == 0:
            messagebox.showinfo(
                "Message", "Camera is already off Please Turn on Camera")
        else:

            self.p.terminate()
            destroy_window()
            self.process_list.remove(self.p)
        # for _ in self.process_list:
        #     if _.is_alive():
        #         _.terminate()
        #     else:
        #         pass
        # if self.p is not None:

        #     if self.p.is_alive():
        #         self.p.kill()
        #         self.p=None
        #         messagebox.showinfo("Message", "Camera Turned off")
        #     else:
        #         pass
        # else:
        #     messagebox.showinfo("Message", "Please Turn on camera first")

    def show_images_on_dash(self):
        self.frame2.destroy()
        self.create_right_frame()

        img_frame = ctk.CTkFrame(
            self.frame2, corner_radius=30, fg_color="white")
        img_frame.pack(anchor="center", expand="true",
                       padx=(20, 20), pady=(20, 20), fill="both")

        frame2 = ctk.CTkFrame(img_frame, corner_radius=30,
                              height=60, fg_color="white")
        frame2.pack(side="bottom", fill="x", padx=(20, 20), pady=(5, 30), )

        prev_btn = ctk.CTkButton(frame2, text="Previous", border_width=1, corner_radius=20, height=40,
                                 fg_color=self.fg_color, hover_color=self.hover_color, command=self.prev_rotate_img)
        prev_btn.pack(side="left", padx=(20, 10), pady=(10, 10), expand="true")

        delete_btn = ctk.CTkButton(frame2, text="Delete", fg_color=self.fg_color, border_width=1, height=40,
                                   corner_radius=20, hover_color=self.hover_color, command=self.delete_current_img)
        delete_btn.pack(side="left", padx=(10, 10),
                        pady=(10, 10), expand="true")

        delete_all = ctk.CTkButton(frame2, text="Delete All", height=40, fg_color=self.fg_color, border_width=1,
                                   corner_radius=20, hover_color=self.hover_color, command=self.delete_images_all)
        delete_all.pack(side="left", padx=(10, 10),
                        pady=(10, 10), expand="true")

        next_btn = CTkButton(frame2, text="next", height=40, border_width=1, fg_color=self.fg_color, corner_radius=20,
                             hover_color=self.hover_color, command=self.rotate_img)
        next_btn.pack(side="left", padx=(10, 20), pady=(10, 10), expand="true")

        self.show_imag(img_frame)

    def prev_rotate_img(self):

        if self.counter == 0:
            messagebox.showinfo("Images Ended", "No previous Image Aviable")
        elif self.counter < 0:
            self.counter = 0
        else:
            self.counter -= 1
            self.img_label.configure(
                image=self.img_array[self.counter % len(self.img_array)])

    def rotate_img(self):
        if self.counter < 0 or self.counter >= len(self.img_array) - 1:
            self.counter = 0
        else:
            self.counter += 1

        print(self.counter)
        self.img_label.configure(
            image=self.img_array[self.counter])

    def delete_images_all(self):
        directory_path = "output_images"
        try:
            query = "delete from images where userid= ?"
            param = (self.__userid,)
            # for filename in os.listdir(directory_path):
            for filename in self.images_list:
                file_path = os.path.join(directory_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            self.img_array.clear()
            self.images_list.clear()

            db = DatabaseConnection()
            db.connect()
            res = db.execute_and_fetch_query(query, False, param)
            if res:
                self.img_label.configure(image="")
                messagebox.showinfo(
                    "Success", "All files deleted successfully.")
            else:
                messagebox.showerror("Error", "Failed to delete all files.")

        except Exception as e:
            messagebox.showerror("Error deleting", f"Error: {e}")

    def delete_current_img(self):
        directory_path = "output_images"
        # current_image = self.img_array[self.counter % len(self.img_array)]
        files = self.images_list

        img_name = files[self.counter % len(self.img_array)]
        image_path = os.path.join(directory_path, img_name)

        print(image_path)
        try:
            # Check if the image exists
            if os.path.exists(image_path):
                # Delete the image file
                os.remove(image_path)
                # Delete the image from the database
                db = DatabaseConnection()
                db.connect()
                query = "DELETE FROM images WHERE images = ? AND userid = ?"
                param = (img_name, self.__userid)
                res = db.execute_and_fetch_query(query, False, param)
                if res:
                    print(f"Image {image_path} deleted successfully.")
                    messagebox.showinfo(
                        "Success", "Image deleted successfully.")
                    if len(self.img_array) > 0:
                        del self.img_array[self.counter % len(self.img_array)]
                        self.rotate_img()
                    else:
                        messagebox.showinfo(
                            "Success", "No more images to show.")

            else:
                print(f"Image {image_path} does not exist.")
        except Exception as e:
            print(f"Error deleting image {image_path}: {str(e)}")
            messagebox.showerror("Error deleting", f"Error: {e}")

        # self.show_imag(self.frame2)

    def show_imag(self, frame2):

        def fun():
            q = "select images from images where userid=?"
            params = (self.__userid,)
            db = DatabaseConnection()
            db.connect()
            result = db.execute_and_fetch_query(q, True, params)
            if result:
                self.images_list = [row[0] for row in result]

                self.counter = 0
                # files = os.listdir("output_images")
                # files = self.images_list

                self.img_array = []
                for file in self.images_list:
                    img = PIL.Image.open(os.path.join('output_images', file))
                    img_resize = img.resize((850, 450))
                    self.img_array.append(ImageTk.PhotoImage(img_resize))

                self.img_label = ctk.CTkLabel(
                    frame2, text="", image=self.img_array[0], corner_radius=30, )
                self.img_label.pack(anchor="n", pady=(25, 0), fill="both")
            else:
                messagebox.showerror("Error", "No Image Found Turn on Camera")

        p = threading.Thread(target=fun, daemon=True)
        p.start()

    def theme_mode(self):
        self.frame2.destroy()
        self.create_right_frame()
        self.create_theme_frame(self.frame2)

    def create_theme_frame(self, frames):

        img2 = ctk.CTkImage(light_image=PIL.Image.open("images/sk.jpg"), dark_image=PIL.Image.open("images/sk.jpg"),
                            size=(1366, 768))
        # img1 = ImageTk.PhotoImage(PIL.Image.open("images/sk.jpg"))

        img_label = CTkLabel(master=frames, image=img2)
        img_label.pack()

        theme_frame = ctk.CTkFrame(
            frames, border_width=1, corner_radius=0, width=350, height=400)
        theme_frame.place(relx=0.5, anchor="center", rely=0.5)

        theme_label = CTkLabel(theme_frame, corner_radius=0, text="Themes")
        theme_label.place(anchor="center", relx=0.5, rely=0.15)

        self.switch = ctk.CTkSwitch(theme_frame, text="Theme Mode", command=self.switch_event,
                                    onvalue=1, offvalue=0)
        self.switch.place(relheight=0.2, relx=0.5, anchor="center", rely=0.3)

        theme_color_label = CTkLabel(
            theme_frame, corner_radius=0, text="Themes Colors")
        theme_color_label.place(relheight=0.2, relx=0.5,
                                anchor="center", rely=0.48)

        # self.optionmenu = ctk.CTkSegmentedButton(theme_frame, values=["Green", "Dark-Blue", "Blue"], width=200,
        #                                          height=40, unselected_hover_color=self.hover_color,
        #                                          command=self.segmented_button_callback)
        # self.optionmenu.place(relx=0.51, anchor="center", rely=0.65)

        # self.change = ctk.CTkButton(theme_frame, fg_color=self.fg_color, corner_radius=20, text="change",
        #                             command=self.changetheme, hover_color=self.hover_color, width=150, height=40)
        # self.change.place(anchor="center", relx=0.51, rely=0.85)

    def switch_event(self):
        if self.switch.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("light")

    def segmented_button_callback(self, values):
        values = values.lower()
        if values == "green":
            self.theme_color_default = "green"

        elif values == "blue":
            self.theme_color_default = "blue"
        elif values == "dark-blue":
            self.theme_color_default = "dark-blue"
        else:
            pass

    def changetheme(self):
        if self.theme_color_default == "":
            messagebox.showinfo("Please", "Please Select theme color")

        else:
            color = self.theme_color_default
            self.root.destroy()

            roots = ctk.CTk()
            ctk.set_default_color_theme(color)
            dashboard(roots)
            roots.mainloop()

    def logout_fun(self):
        self.frame2.destroy()
        self.left_frame.destroy()
        self.create_log_frame()
        self.create_right_frame()

        # self.left_frame.destroy()

    def show_updation_data_frame2(self):
        img2 = ctk.CTkImage(light_image=PIL.Image.open("images/sk.jpg"), dark_image=PIL.Image.open("images/sk.jpg"),
                            size=(1366, 768))
        # img1 = ImageTk.PhotoImage(PIL.Image.open("images/sk.jpg"))

        img_label = CTkLabel(master=self.frame2, image=img2)
        img_label.pack()

        frame1 = ctk.CTkFrame(self.frame2, width=700, height=500)
        frame1.place(anchor="center", relx=0.5, rely=0.5)

        self.logo_profile = ctk.CTkLabel(
            frame1,
            text="Update Profile",
            font=("times new roman", 20, "bold")

        )
        self.logo_profile.place(relx=0.5, rely=0.1, anchor="center")

        ctk.CTkLabel(
            frame1,
            text="First Name",
            font=("times new roman", 14, "bold"),
        ).place(relx=0.1, rely=0.2)
        self.txt_fname = CTkEntry(frame1, font=(
            "times new roman", 15), width=250, corner_radius=0, height=30, placeholder_text=self.__userdata[1])
        self.txt_fname.place(relx=0.1, rely=0.25)

        # last name
        CTkLabel(
            frame1,
            text="Last Name",
            font=("times new roman", 13, "bold"),
        ).place(relx=0.55, rely=0.2)
        self.txt_lname = CTkEntry(frame1, font=(
            "times new roman", 15), width=250, height=30, corner_radius=0, placeholder_text=self.__userdata[2])
        self.txt_lname.place(relx=0.55, rely=0.25)

        # ===
        # contact
        CTkLabel(
            frame1,
            text="Contact No",
            font=("times new roman", 13, "bold"), fg_color="transparent"
        ).place(relx=0.1, rely=0.35)
        self.txt_contact = CTkEntry(frame1, font=(
            "times new roman", 15), width=250, corner_radius=0, placeholder_text=self.__userdata[3], height=30)
        self.txt_contact.place(relx=0.1, rely=0.4)

        # Email
        CTkLabel(
            frame1,
            text="Email",
            font=("times new roman", 13, "bold"), fg_color="transparent"

        ).place(relx=0.55, rely=0.35)
        self.txt_email = CTkEntry(frame1, font=(
            "times new roman", 15), width=250, corner_radius=0, placeholder_text=self.__userdata[4], height=30)
        self.txt_email.place(relx=0.55, rely=0.4)

        # Security Question
        CTkLabel(
            frame1,
            text="Security Question", fg_color="transparent",
            font=("times new roman", 13, "bold"),

        ).place(relx=0.1, rely=0.5)

        self.cmb_ques = ctk.CTkComboBox(master=frame1,
                                        values=[
                                            "Your First Pet Name", "Your Birth Place", "Your Best Friend Name"],
                                        dropdown_hover_color=self.hover_color,
                                        width=250, height=30, corner_radius=0, state="readonly",
                                        font=("times new roman", 15))
        self.cmb_ques.set(self.__userdata[5])
        self.cmb_ques.place(relx=0.1, rely=0.55)

        # Answer
        CTkLabel(
            frame1,
            text="Answer",
            font=("times new roman", 13, "bold")
        ).place(relx=0.55, rely=0.5)
        self.txt_answer = CTkEntry(frame1, font=(
            "times new roman", 15), corner_radius=0, placeholder_text=self.__userdata[6], width=250, height=30)
        self.txt_answer.place(relx=0.55, rely=0.55)

        # ===
        # contact
        CTkLabel(
            frame1,
            text="Password",
            font=("times new roman", 13, "bold"), fg_color="transparent"

        ).place(relx=0.1, rely=0.65)
        self.txt_pass = CTkEntry(frame1, font=(
            "times new roman", 15), corner_radius=0, placeholder_text=self.__userdata[7], show="*", width=250,
            height=30)
        self.txt_pass.place(relx=0.1, rely=0.7)

        # Email
        CTkLabel(
            frame1,
            text="Confirm Password",
            font=("times new roman", 15, "bold"),

        ).place(relx=0.55, rely=0.65)
        self.txt_cpass = CTkEntry(frame1, font=(
            "times new roman", 15), corner_radius=0, placeholder_text=self.__userdata[7], show="*", width=250,
            height=30)
        self.txt_cpass.place(relx=0.55, rely=0.7, )

        self.btn = ctk.CTkButton(
            frame1,
            text="Update Now",
            font=("times new roman", 15, "bold"),
            corner_radius=30,
            cursor="hand2",
            command=self.update_data,
            width=150, height=40, hover_color=self.hover_color, fg_color=self.fg_color,
        )
        self.btn.place(relx=0.5, rely=0.9, anchor="center")

    def register_data(self):
        img2 = ctk.CTkImage(light_image=PIL.Image.open("images/sk.jpg"), dark_image=PIL.Image.open("images/sk.jpg"),
                            size=(1366, 768))
        # img1 = ImageTk.PhotoImage(PIL.Image.open("images/sk.jpg"))

        img_label = CTkLabel(master=self.frame2, image=img2)
        img_label.pack()

        frame1 = ctk.CTkFrame(self.frame2, width=700, height=500)
        frame1.place(anchor="center", relx=0.5, rely=0.5)

        ctk.CTkLabel(
            frame1,
            text="Registration",
            font=("times new roman", 20, "bold")
        ).place(relx=0.5, rely=0.1, anchor="center")

        ctk.CTkLabel(
            frame1,
            text="First Name",
            font=("times new roman", 14, "bold"),
        ).place(relx=0.1, rely=0.2)
        self.txt_fname = CTkEntry(frame1, font=(
            "times new roman", 15), width=250, corner_radius=0, height=30, placeholder_text="Enter first name")
        self.txt_fname.place(relx=0.1, rely=0.25)

        # last name
        CTkLabel(
            frame1,
            text="Last Name",
            font=("times new roman", 13, "bold"),
        ).place(relx=0.55, rely=0.2)
        self.txt_lname = CTkEntry(frame1, font=(
            "times new roman", 15), width=250, height=30, corner_radius=0, placeholder_text="Enter last name")
        self.txt_lname.place(relx=0.55, rely=0.25)

        # ===
        # contact
        CTkLabel(
            frame1,
            text="Contact No",
            font=("times new roman", 13, "bold"), fg_color="transparent"
        ).place(relx=0.1, rely=0.35)
        self.txt_contact = CTkEntry(frame1, font=(
            "times new roman", 15), width=250, corner_radius=0, placeholder_text="Enter contact no", height=30)
        self.txt_contact.place(relx=0.1, rely=0.4)

        # Email
        CTkLabel(
            frame1,
            text="Email",
            font=("times new roman", 13, "bold"), fg_color="transparent"

        ).place(relx=0.55, rely=0.35)
        self.txt_email = CTkEntry(frame1, font=(
            "times new roman", 15), width=250, corner_radius=0, placeholder_text="Enter Email", height=30)
        self.txt_email.place(relx=0.55, rely=0.4)

        # Security Question
        CTkLabel(
            frame1,
            text="Security Question", fg_color="transparent",
            font=("times new roman", 13, "bold"),

        ).place(relx=0.1, rely=0.5)

        self.cmb_ques = ctk.CTkComboBox(master=frame1,
                                        values=[
                                            "Your First Pet Name", "Your Birth Place", "Your Best Friend Name"],
                                        dropdown_hover_color=self.hover_color,
                                        width=250, height=30, corner_radius=0, state="readonly",
                                        font=("times new roman", 15))
        self.cmb_ques.set("select")
        self.cmb_ques.place(relx=0.1, rely=0.55)

        # Answer
        CTkLabel(
            frame1,
            text="Answer",
            font=("times new roman", 13, "bold")
        ).place(relx=0.55, rely=0.5)
        self.txt_answer = CTkEntry(frame1, font=(
            "times new roman", 15), corner_radius=0, placeholder_text="Answer", width=250, height=30)
        self.txt_answer.place(relx=0.55, rely=0.55)

        # ===
        # contact
        CTkLabel(
            frame1,
            text="Password",
            font=("times new roman", 13, "bold"), fg_color="transparent"

        ).place(relx=0.1, rely=0.65)
        self.txt_pass = CTkEntry(frame1, font=(
            "times new roman", 15), corner_radius=0, placeholder_text="Password", show="*", width=250, height=30)
        self.txt_pass.place(relx=0.1, rely=0.7)

        # Email
        CTkLabel(
            frame1,
            text="Confirm Password",
            font=("times new roman", 15, "bold"),

        ).place(relx=0.55, rely=0.65)
        self.txt_cpass = CTkEntry(frame1, font=(
            "times new roman", 15), corner_radius=0, placeholder_text="Confirm Password", show="*", width=250,
            height=30)
        self.txt_cpass.place(relx=0.55, rely=0.7, )

        btn = ctk.CTkButton(
            frame1,
            text="Register Now",
            font=("times new roman", 15, "bold"),
            corner_radius=30,
            cursor="hand2",
            command=self.registration_data,
            width=150, height=40, hover_color=self.hover_color, fg_color=self.fg_color,
        )
        btn.place(relx=0.5, rely=0.9, anchor="center")

    def registration_data(self):
        def fun():
            user = admin()
            user.setname(self.txt_fname.get().strip().lower() +
                         " " + self.txt_lname.get().strip().lower())
            user.setemail(self.txt_email.get().strip())
            if self.txt_pass.get() == self.txt_cpass.get() and len(self.txt_pass.get()) == len(self.txt_cpass.get()):
                user.setpassword(self.txt_pass.get().strip())
            else:
                messagebox.showerror("Password Matching Error",
                                     "Password and Confirm Password did not Match")
            user.setquest(self.cmb_ques.get().strip().lower())
            user.setanswer(self.txt_answer.get().strip().lower())
            user.setcontact(self.txt_contact.get().strip())
            result = user.insert()
            if result:
                messagebox.showinfo("Message", "Sucessfully Registered")
                self.login_fun()
                # self.left_frame.destroy()
                # self.frame2.destroy()
                # self.create_left_frame()
                # self.create_right_frame()
            else:
                pass
        p = threading.Thread(target=fun)
        p.daemon = True
        p.start()

    def update_data(self):
        def fun():
            user = admin()
            user.setname(
                f"{self.txt_fname.get().strip()} {self.txt_lname.get().strip()}")
            user.setemail(self.txt_email.get().strip())
            if self.txt_pass.get() == self.txt_cpass.get() and len(self.txt_pass.get()) == len(self.txt_cpass.get()):
                user.setpassword(self.txt_pass.get().strip())
                user.setquest(self.cmb_ques.get().strip().lower())
                user.setanswer(self.txt_answer.get().strip().lower())
                user.setcontact(self.txt_contact.get().strip())
                print(self.__userid)
                print(self.__userdata)
                user.setid(self.__userid)
                result = user.update()
                if result:
                    self.user_data()
                    self.show_updation_data_frame2()
                    messagebox.showinfo(
                        "Message", "Sucessfully Update user details")
                else:
                    pass

                print(self.__userdata)

            else:
                messagebox.showerror("Password Matching Error",
                                     "Password and Confirm Password did not Match")
        threading.Thread(target=fun, daemon=True).start()

    def user_data(self):
        print(self.__userid)
        query = 'select * from registration where id = ?'
        param = (self.__userid,)
        self.db = DatabaseConnection()
        self.db.connect()
        result = self.db.execute_and_fetch_query(
            query=query, fetch=True, params=param)

        for index, row in enumerate(result):
            if index == 0:  # Check if it's the first tuple in the list
                # Split the name at the second index
                name_parts = row[1].split()
                result[index] = (row[0],) + tuple(name_parts) + row[2:]
        self.__userdata = list(chain(*result))


# root = ctk.CTk()
# dashboard(root)
# root.mainloop()
