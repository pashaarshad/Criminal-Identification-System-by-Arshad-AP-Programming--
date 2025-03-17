import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk
import threading
import shutil
import sqlite3
import cv2
import os
from playsound import playsound  # Add this import
from facerec import *
from register import *
from dbHandler import *
import threading  # Add this import for threading
import mainsms  # Add this import for sending SMS
import datetime  # Add this import for current time
import socket  # Add this import for current location

active_page = 0
thread_event = None
left_frame = None
right_frame = None
heading = None
webcam = None
img_label = None
img_read = None
img_list = []
slide_caption = None
slide_control_panel = None
current_slide = -1

# Define common button style
BUTTON_STYLE = {
    'font': "Arial 12 bold",
    'bg': "#2196f3",
    'fg': "white",
    'bd': 0,
    'highlightthickness': 0,
    'activebackground': "#90ceff",
    'activeforeground': "white",
    'relief': "flat",
    'padx': 20,
    'pady': 10
}

root = tk.Tk()
root.geometry("1500x900+200+100")

# create Pages
pages = []
for i in range(4):
    pages.append(tk.Frame(root, bg="#373836"))
    pages[i].pack(side="top", fill="both", expand=True)
    pages[i].place(x=0, y=0, relwidth=1, relheight=1)


def goBack():
    global active_page, thread_event, webcam

    if (active_page==3 and not thread_event.is_set()):
        thread_event.set()
        webcam.release()

    for widget in pages[active_page].winfo_children():
        widget.destroy()

    pages[0].lift()
    active_page = 0


def basicPageSetup(pageNo):
    global left_frame, right_frame, heading

    back_img = tk.PhotoImage(file="back.png")
    back_button = tk.Button(pages[pageNo], image=back_img, bg="#373836", bd=0, highlightthickness=0,
           activebackground="#373836", command=goBack)
    back_button.image = back_img
    back_button.place(x=10, y=10)

    heading = tk.Label(pages[pageNo], fg="white", bg="#373836", font="Arial 20 bold", pady=10)
    heading.pack()

    content = tk.Frame(pages[pageNo], bg="#373836", pady=20)
    content.pack(expand="true", fill="both")

    left_frame = tk.Frame(content, bg="#373836")
    left_frame.grid(row=0, column=0, sticky="nsew")

    right_frame = tk.LabelFrame(content, text="Detected Criminals", bg="#373836", font="Arial 20 bold", bd=4,
                             foreground="#2ea3ef", labelanchor="n")
    right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    content.grid_columnconfigure(0, weight=1, uniform="group1")
    content.grid_columnconfigure(1, weight=1, uniform="group1")
    content.grid_rowconfigure(0, weight=1)


def showImage(frame, img_size):
    global img_label, left_frame

    img = cv2.resize(frame, (img_size, img_size))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)
    if (img_label == None):
        img_label = tk.Label(left_frame, image=img, bg="#373836")
        img_label.image = img
        img_label.pack(padx=20)
    else:
        img_label.configure(image=img)
        img_label.image = img


def getNewSlide(control):
    global img_list, current_slide

    if(len(img_list) > 1):
        if(control == "prev"):
            current_slide = (current_slide-1) % len(img_list)
        else:
            current_slide = (current_slide+1) % len(img_list)

        img_size = left_frame.winfo_height() - 200
        showImage(img_list[current_slide], img_size)

        slide_caption.configure(text = "Image {} of {}".format(current_slide+1, len(img_list)))


def selectMultiImage(opt_menu, menu_var):
    global img_list, current_slide, slide_caption, slide_control_panel

    filetype = [("images", "*.jpg *.jpeg *.png")]
    path_list = filedialog.askopenfilenames(title="Choose atleast 5 images", filetypes=filetype)

    if(len(path_list) < 5):
        messagebox.showerror("Error", "Choose atleast 5 images.")
    else:
        img_list = []
        current_slide = -1

        # Resetting slide control panel
        if (slide_control_panel != None):
            slide_control_panel.destroy()

        # Creating Image list
        for path in path_list:
            img_list.append(cv2.imread(path))

        # Creating choices for profile pic menu
        menu_var.set("")
        opt_menu['menu'].delete(0, 'end')

        for i in range(len(img_list)):
            ch = "Image " + str(i+1)
            opt_menu['menu'].add_command(label=ch, command= tk._setit(menu_var, ch))
            menu_var.set("Image 1")


        # Creating slideshow of images
        img_size =  left_frame.winfo_height() - 200
        current_slide += 1
        showImage(img_list[current_slide], img_size)

        slide_control_panel = tk.Frame(left_frame, bg="#373836", pady=20)
        slide_control_panel.pack()

        back_img = tk.PhotoImage(file="previous.png")
        next_img = tk.PhotoImage(file="next.png")

        prev_slide = tk.Button(slide_control_panel, image=back_img, bg="#373836", bd=0, highlightthickness=0,
                            activebackground="#373836", command=lambda : getNewSlide("prev"))
        prev_slide.image = back_img
        prev_slide.grid(row=0, column=0, padx=60)

        slide_caption = tk.Label(slide_control_panel, text="Image 1 of {}".format(len(img_list)), fg="#ff9800",
                              bg="#373836", font="Arial 15 bold")
        slide_caption.grid(row=0, column=1)

        next_slide = tk.Button(slide_control_panel, image=next_img, bg="#373836", bd=0, highlightthickness=0,
                            activebackground="#373836", command=lambda : getNewSlide("next"))
        next_slide.image = next_img
        next_slide.grid(row=0, column=2, padx=60)


def register(entries, required, menu_var):
    global img_list

    # Checking if no image selected
    if(len(img_list) == 0):
        messagebox.showerror("Error", "Select Images first.")
        return

    # Fetching data from entries
    entry_data = {}
    for i, entry in enumerate(entries):
        val = entry[1].get()

        if (len(val) == 0 and required[i] == 1):
            messagebox.showerror("Field Error", "Required field missing :\n\n%s" % (entry[0]))
            return
        else:
            entry_data[entry[0]] = val.lower()

    # Ensure 'face_samples' directory exists
    if not os.path.isdir('face_samples'):
        os.mkdir('face_samples')

    # Setting Directory
    path = os.path.join('face_samples', "temp_criminal")
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    os.mkdir(path)

    no_face = []
    for i, img in enumerate(img_list):
        # Storing Images in directory
        id = registerCriminal(img, path, i + 1)
        if(id != None):
            no_face.append(id)

    # check if any image doesn't contain face
    if(len(no_face) > 0):
        no_face_st = ""
        for i in no_face:
            no_face_st += "Image " + str(i) + ", "
        messagebox.showerror("Registration Error", "Registration failed!\n\nFollowing images doesn't contain"
                        " face or Face is too small:\n\n%s"%(no_face_st))
        shutil.rmtree(path, ignore_errors=True)
    else:
        # Storing data in database
        rowId = insertData(entry_data)

        if(rowId > 0):
            messagebox.showinfo("Success", "Criminal Registered Successfully.")
            shutil.move(path, os.path.join('face_samples', entry_data["Name"]))

            # save profile pic
            profile_img_num = int(menu_var.get().split(' ')[1]) - 1
            if not os.path.isdir("profile_pics"):
                os.mkdir("profile_pics")
            cv2.imwrite("profile_pics/criminal %d.png"%rowId, img_list[profile_img_num])

            goBack()
        else:
            shutil.rmtree(path, ignore_errors=True)
            messagebox.showerror("Database Error", "Some error occured while storing data.")


## update scrollregion when all widgets are in canvas
def on_configure(event, canvas, win):
    canvas.configure(scrollregion=canvas.bbox('all'))
    canvas.itemconfig(win, width=event.width)

## Register Page ##
def getPage1():
    global active_page, left_frame, right_frame, heading, img_label
    active_page = 1
    img_label = None
    opt_menu = None
    menu_var = tk.StringVar(root)
    pages[1].lift()

    basicPageSetup(1)
    heading.configure(text="Register Criminal")
    right_frame.configure(text="Enter Details")

    btn_grid = tk.Frame(left_frame, bg="#373836")
    btn_grid.pack()

    tk.Button(btn_grid, text="Select Images", command=lambda: selectMultiImage(opt_menu, menu_var), **BUTTON_STYLE).grid(row=0, column=0, padx=25, pady=25)


    # Creating Scrollable Frame
    canvas = tk.Canvas(right_frame, bg="#373836", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand="true", padx=30)
    scrollbar = tk.Scrollbar(right_frame, command=canvas.yview, width=20, troughcolor="#373836", bd=0,
                          activebackground="#00bcd4", bg="#2196f3", relief="raised")
    scrollbar.pack(side="left", fill="y")

    scroll_frame = tk.Frame(canvas, bg="#373836", pady=20)
    scroll_win = canvas.create_window((0, 0), window=scroll_frame, anchor='nw')

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda event, canvas=canvas, win=scroll_win: on_configure(event, canvas, win))


    tk.Label(scroll_frame, text="* Required Fields", bg="#373836", fg="yellow", font="Arial 13 bold").pack()
    # Adding Input Fields
    input_fields = ("Name", "Father's Name", "Mother's Name", "Gender", "DOB(yyyy-mm-dd)", "Blood Group",
                    "Identification Mark", "Nationality", "Religion", "Crimes Done", "Profile Image")
    ip_len = len(input_fields)
    required = [1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0]

    entries = []
    for i, field in enumerate(input_fields):
        row = tk.Frame(scroll_frame, bg="#373836")
        row.pack(side="top", fill="x", pady=15)

        label = tk.Text(row, width=20, height=1, bg="#373836", fg="#ffffff", font="Arial 13", highlightthickness=0, bd=0)
        label.insert("insert", field)
        label.pack(side="left")

        if(required[i] == 1):
            label.tag_configure("star", foreground="yellow", font="Arial 13 bold")
            label.insert("end", "  *", "star")
        label.configure(state="disabled")

        if(i != ip_len-1):
            ent = tk.Entry(row, font="Arial 13", selectbackground="#90ceff")
            ent.pack(side="right", expand="true", fill="x", padx=10)
            entries.append((field, ent))
        else:
            menu_var.set("Image 1")
            choices = ["Image 1"]
            opt_menu = tk.OptionMenu(row, menu_var, *choices)
            opt_menu.pack(side="right", fill="x", expand="true", padx=10)
            opt_menu.configure(font="Arial 13", bg="#2196f3", fg="white", bd=0, highlightthickness=0, activebackground="#90ceff")
            menu = opt_menu.nametowidget(opt_menu.menuname)
            menu.configure(font="Arial 13", bg="white", activebackground="#90ceff", bd=0)

    tk.Button(scroll_frame, text="Register", command=lambda: register(entries, required, menu_var), **BUTTON_STYLE).pack(pady=25)


def showCriminalProfile(name):
    global right_frame, scroll_frame

    print(f"Showing profile for: {name}")  # Debug log
    
    for widget in scroll_frame.winfo_children():
        widget.destroy()

    # Retrieve data based on name or ID
    (id, crim_data) = retrieveData(name)

    if id is None or crim_data is None:
        messagebox.showerror("Error", f"No data found for criminal: {name}")
        return

    path = os.path.join("profile_pics", "criminal %d.png" % id)
    profile_img = cv2.imread(path)

    if profile_img is None:
        messagebox.showerror("Error", "Profile image not found.")
        return

    profile_img = cv2.resize(profile_img, (300, 300))
    img = cv2.cvtColor(profile_img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)
    img_label = tk.Label(scroll_frame, image=img, bg="#373836")
    img_label.image = img
    img_label.grid(row=0, column=0, columnspan=2, pady=20)

    for i, item in enumerate(crim_data.items()):
        tk.Label(scroll_frame, text=item[0], pady=5, fg="yellow", font="Arial 12 bold", bg="#373836").grid(row=i+1, column=0, sticky='w', padx=10)
        tk.Label(scroll_frame, text=":", fg="yellow", padx=10, font="Arial 12 bold", bg="#373836").grid(row=i+1, column=1)
        val = "---" if (item[1] == "") else item[1]
        tk.Label(scroll_frame, text=val.capitalize(), fg="white", font="Arial 12", bg="#373836").grid(row=i+1, column=2, sticky='w')


def send_sms(criminal_name):
    # Retrieve criminal details
    _, crim_data = retrieveData(criminal_name)
    
    if crim_data is None:
        messagebox.showerror("Error", f"No data found for criminal: {criminal_name}")
        return

    # Format the message
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    current_location = "Hunsu Station, Airport, Live"
    
    message = f"Criminal Detected: {criminal_name}\n"
    message += f"Location: {current_location}\n"
    message += f"Time: {current_time}\n"
    message += f"Date: {current_date}\n\n"
    message += "Profile Details:\n"
    
    for key, value in crim_data.items():
        message += f"{key}: {value.capitalize() if value else '---'}\n"
    
    # Send the SMS
    mainsms.send_sms(message)


def startRecognition():
    global img_read, img_label, scroll_frame

    if(img_label == None):
        messagebox.showerror("Error", "No image selected. ")
        return

    for wid in scroll_frame.winfo_children():
        wid.destroy()

    frame = cv2.flip(img_read, 1, 0)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    face_coords = detect_faces(gray_frame)

    if (len(face_coords) == 0):
        messagebox.showerror("Error", "Image doesn't contain any face or face is too small.")
    else:
        (model, names) = train_model()
        print('Training Successful. Detecting Faces')
        (frame, recognized) = recognize_face(model, frame, gray_frame, face_coords, names)

        # Play beep sound immediately when faces are recognized
        if len(recognized) > 0:
            threading.Thread(target=playBeepSound).start()
            for crim in recognized:
                send_sms(crim[0])  # Send SMS for each recognized criminal

        img_size = left_frame.winfo_height() - 40
        frame = cv2.flip(frame, 1, 0)
        showImage(frame, img_size)

        if (len(recognized) == 0):
            messagebox.showerror("Error", "No criminal recognized.")
            return

        for _, crim in enumerate(recognized):
            crim_label = tk.Label(scroll_frame, text=crim[0], bg="orange", font="Arial 15 bold", pady=20)
            crim_label.pack(fill="x", padx=20, pady=10)
            crim_label.bind("<Button-1>", lambda _e, name=crim[0]: showCriminalProfile(name))


def selectImage():
    global left_frame, img_label, img_read
    for wid in scroll_frame.winfo_children():
        wid.destroy()

    filetype = [("images", "*.jpg *.jpeg *.png")]
    path = filedialog.askopenfilename(title="Choose a image", filetypes=filetype)

    if(len(path) > 0):
        img_read = cv2.imread(path)

        img_size =  left_frame.winfo_height() - 40
        showImage(img_read, img_size)


## Detection Page ##
def getPage2():
    global active_page, left_frame, right_frame, img_label, heading, scroll_frame
    img_label = None
    active_page = 2
    pages[2].lift()

    basicPageSetup(2)
    heading.configure(text="Detect Criminal")
    right_frame.configure(text="Detected Criminals (Click to view profile)")

    btn_grid = tk.Frame(left_frame, bg="#373836")
    btn_grid.pack()

    tk.Button(btn_grid, text="Select Image", command=selectImage, **BUTTON_STYLE).grid(row=0, column=0, padx=25, pady=25)
    tk.Button(btn_grid, text="Recognize", command=startRecognition, **BUTTON_STYLE).grid(row=0, column=1, padx=25, pady=25)

    # Add scrollbar to right_frame
    canvas = tk.Canvas(right_frame, bg="#373836", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
    scrollbar = tk.Scrollbar(right_frame, command=canvas.yview, width=20, troughcolor="#373836", bd=0,
                             activebackground="#00bcd4", bg="#2196f3", relief="raised")
    scrollbar.pack(side="right", fill="y")

    scroll_frame = tk.Frame(canvas, bg="#373836")
    scroll_win = canvas.create_window((0, 0), window=scroll_frame, anchor='nw')

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda event, canvas=canvas, win=scroll_win: on_configure(event, canvas, win))

    # Update scrollregion when all widgets are in canvas
    scroll_frame.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))


def videoLoop(model, names):
    global thread_event, left_frame, webcam, img_label
    webcam = cv2.VideoCapture(0)
    old_recognized = []
    img_label = None

    try:
        while not thread_event.is_set():
            # Loop until the camera is working
            while (True):
                # Put the image from the webcam into 'frame'
                (return_val, frame) = webcam.read()
                if (return_val == True):
                    break
                else:
                    print("Failed to open webcam. Trying again...")

            # Flip the image (optional)
            frame = cv2.flip(frame, 1, 0)
            # Convert frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect Faces
            face_coords = detect_faces(gray_frame)
            (frame, recognized) = recognize_face(model, frame, gray_frame, face_coords, names)

            # Play beep sound immediately when new faces are recognized
            recog_names = [item[0] for item in recognized]
            if recognized and recog_names != old_recognized:
                threading.Thread(target=playBeepSound).start()
                for crim in recognized:
                    send_sms(crim[0])  # Send SMS for each recognized criminal

            if(recog_names != old_recognized):
                for wid in right_frame.winfo_children():
                    wid.destroy()

                for i, crim in enumerate(recognized):
                    crim_label = tk.Label(right_frame, text=crim[0], bg="orange", font="Arial 15 bold", pady=20)
                    crim_label.pack(fill="x", padx=20, pady=10)
                    crim_label.bind("<Button-1>", lambda e, name=crim[0]: showCriminalProfile(name))

                old_recognized = recog_names

            # Display Video stream
            img_size = min(left_frame.winfo_width(), left_frame.winfo_height()) - 20

            showImage(frame, img_size)

    except RuntimeError:
        print("[INFO]Caught Runtime Error")
    except tk.TclError:
        print("[INFO]Caught Tcl Error")


## video surveillance Page ##
def getPage3():
    global active_page, video_loop, left_frame, right_frame, thread_event, heading
    active_page = 3
    pages[3].lift()

    basicPageSetup(3)
    heading.configure(text="Video Surveillance")
    right_frame.configure(text="Detected Criminals")
    left_frame.configure(pady=40)

    (model, names) = train_model()
    print('Training Successful. Detecting Faces')

    thread_event = threading.Event()
    thread = threading.Thread(target=videoLoop, args=(model, names))
    thread.start()


######################################## Home Page ####################################
# Create main container
main_container = tk.Frame(pages[0], bg="#373836")
main_container.pack(expand=True, fill="both")

# Title at top
title_label = tk.Label(main_container, 
                      text="AeroVision Face Detect",
                      fg="white",
                      bg="#373836",
                      font="Arial 35 bold")
title_label.pack(pady=30)

# Create horizontal split container
split_container = tk.Frame(main_container, bg="#373836")
split_container.pack(expand=True, fill="both", padx=50)

# Configure split container columns
split_container.grid_columnconfigure(0, weight=1)  # Left side
split_container.grid_columnconfigure(1, weight=1)  # Right side

# Left side - Logo
left_frame = tk.Frame(split_container, bg="#373836")
left_frame.grid(row=0, column=0, sticky="nsew")

logo = tk.PhotoImage(file="logo.png")
logo_label = tk.Label(left_frame,
                     image=logo,
                     bg="#373836")
logo_label.pack(expand=True, pady=20)

# Right side - Buttons
right_frame = tk.Frame(split_container, bg="#373836")
right_frame.grid(row=0, column=1, sticky="nsew")

# Create a container for buttons to enable center alignment
button_container = tk.Frame(right_frame, bg="#373836")
button_container.place(relx=0.5, rely=0.5, anchor="center")

# Button styles - Gradient-like colors for each button
button_styles = [
    {"bg": "#1a237e", "activebg": "#283593", "hoverbg": "#3949ab"},
     {"bg": "#1a237e", "activebg": "#283593", "hoverbg": "#3949ab"},
        {"bg": "#1a237e", "activebg": "#283593", "hoverbg": "#3949ab"}  
]

buttons = [
    ("Register Criminal", getPage1),
    ("Detect Criminal", getPage2),
    ("Video Surveillance", getPage3)
]

# Create buttons with hover effect
def on_enter(e, hoverbg):
    e.widget['background'] = hoverbg

def on_leave(e, normalbg):
    e.widget['background'] = normalbg

for i, (text, command) in enumerate(buttons):
    style = button_styles[i]
    btn = tk.Button(button_container,
                   text=text,
                   command=command,
                   width=17,
                   **BUTTON_STYLE)
    btn.pack(pady=20)
    
    # Bind hover events
    btn.bind("<Enter>", lambda e, hbg=style["hoverbg"]: on_enter(e, hbg))
    btn.bind("<Leave>", lambda e, nbg=style["bg"]: on_leave(e, nbg))


def retrieveData(name):
    print(f"Attempting to retrieve data for name: {name}")  # Debug log
    
    try:
        conn = sqlite3.connect('criminals.db')
        cursor = conn.cursor()
        
        # Use case-insensitive comparison
        cursor.execute("SELECT * FROM criminaldata WHERE LOWER(name)=LOWER(?)", (name,))
        data = cursor.fetchone()
        
        print(f"Retrieved data: {data}")  # Debug log
        
        if data is None:
            print("No data found in database")  # Debug log
            return None, None
            
        id = data[0]
        crim_data = {
            "Name": data[1],
            "Father's Name": data[2],
            "Mother's Name": data[3],
            "Gender": data[4],
            "DOB": data[5],
            "Blood Group": data[6],
            "Identification Mark": data[7],
            "Nationality": data[8],
            "Religion": data[9],
            "Crimes Done": data[10]
        }
        
        return id, crim_data
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")  # Debug log
        return None, None
    finally:
        if 'conn' in locals():
            conn.close()


def playBeepSound():
    try:
        playsound('beep.mpeg')
    except Exception as e:
        print("Error playing sound:", str(e))


pages[0].lift()
root.mainloop()
