from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import time
import tkinter as tk
import json
import random

#constants
ASCII = ['  ', '..', '<<', 'cc', '77', '33', 'xx', 'ee', 'kk', '##', '⣿⣿']
CONFIG = '.\\ascii_movie_config.json'


def prepare_config():
    if os.path.exists(CONFIG):
        return
    else:
        create_config()


def create_config():
    conf = {'height': 400,
            'length': 400,
            "video path": "",
            "cover photo": ".\\ASCII_movies.png",
            "logo": ".\\ASCII_logo.png"}
    f = open(CONFIG, 'x')
    f.close()
    with open(CONFIG, 'w') as file:
        json.dump(conf, file)


def get_config():
    with open(CONFIG) as file:
        conf = json.load(file)
    return conf


def save_config(config):
    with open(CONFIG, 'w') as file:
        json.dump(config, file)


def get_random_frame(path):
    video = cv2.VideoCapture(path)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    index = min(random.randint(1, frame_count), frame_count)
    video.set(cv2.CAP_PROP_POS_FRAMES, index-1)
    success, image = video.read()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    im_pil = Image.fromarray(image)
    return im_pil


class AsciiMovie(tk.Tk):
    def __init__(self, parent=None):
        tk.Tk.__init__(self, parent)

        # --- configuration ------------------------------
        self.title('ASCII movie player')
        self.__config = get_config()
        self.geometry(f'{self.__config["length"]}x{self.__config["height"]}')
        self.iconphoto(False, tk.PhotoImage(file=self.__config['logo']))

        # --- variables ----------------------------------
        self.__video_path = tk.StringVar()
        self.__video_path.set(self.__config['video path'])
        self.__video_name = tk.StringVar()
        self.__video_name.set(self.__video_path.get().split('/')[-1])
        self.__is_looped = tk.IntVar()
        self.__is_looped.set(0)
        self.__rotate_right = tk.IntVar()
        self.__rotate_right.set(0)
        self.__rotate_left = tk.IntVar()
        self.__rotate_left.set(0)
        self.__inverse_colours = tk.IntVar()
        self.__inverse_colours.set(0)

        # --- prepare visual -----------------------------
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=20)
        self.rowconfigure(1, weight=1)
        self.grid_propagate(0)

        self.prepare_main_layout()
        self.prepare_file_menu_bar()
        self.prepare_minature()

        self.update()
        print(self.minature_frame.winfo_width())
        print(self.minature_frame.winfo_height())

    def prepare_main_layout(self):
        self.menu_frame = tk.Frame(self, bg='lime')
        self.menu_frame.grid(row=0, column=0, sticky='news')
        self.menu_frame.columnconfigure(0, weight=1)
        self.menu_frame.rowconfigure(0, weight=2)
        self.menu_frame.rowconfigure(1, weight=1)
        self.menu_frame.rowconfigure(2, weight=1)
        self.menu_frame.rowconfigure(3, weight=1)
        self.menu_frame.rowconfigure(4, weight=1)
        self.menu_frame.rowconfigure(5, weight=2)
        self.menu_frame.grid_propagate(0)

        self.minature_frame = tk.Frame(self, bg='black')
        self.minature_frame.grid(row=0, column=1, sticky='news')
        self.minature_frame.rowconfigure(0, weight=1)
        self.minature_frame.columnconfigure(0, weight=1)
        self.minature_frame.grid_propagate(0)

        self.loading_bar_frame = tk.Frame(self, bg='blue')
        self.loading_bar_frame.grid(row=1, column=0, columnspan=2, sticky='news')
        self.loading_bar_frame.grid_propagate(0)
        for n in range(10):
            self.loading_bar_frame.columnconfigure(n, weight=1)

    def prepare_file_menu_bar(self):
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)
        self.menu_bar.add_cascade(label='File', menu=self.prepare_file_menu_cascade(self.menu_bar))

    def prepare_file_menu_cascade(self, parent_menu):
        file_menu = tk.Menu(parent_menu)
        file_menu.add_command(label='Open', command=lambda: print('open'))
        file_menu.add_command(label='Save', command=lambda: print('save'))
        file_menu.add_command(label='Load', command=lambda: print('load'))
        return file_menu

    def prepare_minature(self):
        if self.__video_path.get() == "":
            self.prepare_sandard_minature()
        else:
            self.prepare_custom_minature()

    def prepare_sandard_minature(self):
        self.minature_frame.update()
        image_png = Image.open(self.__config['cover photo']).resize(
            (self.minature_frame.winfo_width(), self.minature_frame.winfo_height()))
        image2 = ImageTk.PhotoImage(image_png)
        image_png.close()
        self.minature_label = tk.Label(self.minature_frame, image=image2, bg='orange')
        self.minature_label.im = image2
        self.minature_label.grid(row=0, column=0, sticky='news')

    def prepare_custom_minature(self):
        self.minature_frame.update()
        image = get_random_frame(self.__config['video path']).resize((self.minature_frame.winfo_width(), self.minature_frame.winfo_height()))
        image2 = ImageTk.PhotoImage(image)
        self.minature_label = tk.Label(self.minature_frame, image=image2, bg='orange')
        self.minature_label.im = image2
        self.minature_label.grid(row=0, column=0, sticky='news')

    def prepare_main_manu(self):
        self.movie_name_label = tk.Label(self.menu_frame, textvaraible=self.__video_name, font=20,
                                         bg='#666699', fg='white')
        self.movie_name_label.grid(row=0, column=0, sticky='news')


class AsciiMoviePlayer(tk.Toplevel):
    def __init__(self, master, **kw):
        tk.Toplevel.__init__(self, master, **kw)
        self.display_frame = tk.Frame(self)




