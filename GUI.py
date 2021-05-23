from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import time
import tkinter as tk
from tkinter import font as tkFont
import json
import random
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
import pickle as rick
import os

# D:/HDD/programowanie_python/DiscordBots/PicturesBot/bad_apple/bad_apple.mp4

#constants
ASCII = ['  ', '..', '<<', 'cc', '77', '33', 'xx', 'ee', 'kk', '##', '⣿⣿']
CONFIG = '.\\ascii_movie_config.json'
LIGHT_GRAY = '#bdbdbd'
GRAY = '#909090'
LILA = '#cc99ff'
PURPLE = '#9966ff'
SOMBRA_PURPLE = '#a350f9'
#HELV_20 = tkFont.Font(family='Helvetica', size=20)
#HELV_14 = tkFont.Font(family='Helvetica', size=14)


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


def get_random_frame(path: str):
    if not os.path.exists(path):
        return None
    if not path.endswith('.mp4'):
        return None
    video = cv2.VideoCapture(path)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    index = min(random.randint(1, frame_count), frame_count)
    video.set(cv2.CAP_PROP_POS_FRAMES, index-1)
    success, image = video.read()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    im_pil = Image.fromarray(image)
    return im_pil.convert('L')


def save_list(frame_list):
    file_path: str = asksaveasfilename(filetypes=(('Pickle files', '.pkl'),))
    if not file_path.endswith('.pkl'):
        file_path += '.pkl'
    with open(file_path, 'wb') as file:
        rick.dump(frame_list, file)


def load_list():
    file_path = askopenfilename(filetypes=(('Pickle files', '.pkl'),))
    if file_path == "":
        return [], ""
    with open(file_path, 'rb') as file:
        try:
            ret = rick.load(file)
        except Exception:
            return [], ""
    return ret, file_path


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
        self.__pixelate_choice = tk.StringVar()
        self.__pixelate_choice.set('20')
        self.__ascii_frames = []
        self.__list_loaded = tk.IntVar(self, 0)

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
        self.prepare_main_manu()
        self.prepare_loading_bar()

    def prepare_main_layout(self):
        self.menu_frame = tk.Frame(self, bg=PURPLE)
        self.menu_frame.grid(row=0, column=0, sticky='news')
        self.menu_frame.columnconfigure(0, weight=1)
        self.menu_frame.rowconfigure(0, weight=2)
        self.menu_frame.rowconfigure(1, weight=1)
        self.menu_frame.rowconfigure(2, weight=1)
        self.menu_frame.rowconfigure(3, weight=1)
        self.menu_frame.rowconfigure(4, weight=1)
        self.menu_frame.rowconfigure(5, weight=1)
        self.menu_frame.rowconfigure(6, weight=2)
        self.menu_frame.grid_propagate(0)

        self.minature_frame = tk.Frame(self, bg='black')
        self.minature_frame.grid(row=0, column=1, sticky='news')
        self.minature_frame.rowconfigure(0, weight=1)
        self.minature_frame.columnconfigure(0, weight=1)
        self.minature_frame.grid_propagate(0)

        self.loading_bar_frame = tk.Frame(self, bg='black')
        self.loading_bar_frame.grid(row=1, column=0, columnspan=2, sticky='news')
        self.loading_bar_frame.grid_propagate(0)
        self.loading_bar_frame.rowconfigure(0, weight=1)
        for n in range(10):
            self.loading_bar_frame.columnconfigure(n, weight=1)

    def prepare_file_menu_bar(self):
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)
        self.menu_bar.add_cascade(label='File', menu=self.prepare_file_menu_cascade(self.menu_bar))

    def prepare_file_menu_cascade(self, parent_menu):
        file_menu = tk.Menu(parent_menu)
        file_menu.add_command(label='Open', command=self.open_file)
        file_menu.add_command(label='Save', command=lambda: save_list(self.__ascii_frames))
        file_menu.add_command(label='Load', command=self.load_from_pickle)
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
        image = get_random_frame(self.__config['video path'])
        if image is None:
            self.prepare_sandard_minature()
            return
        image = image.resize((self.minature_frame.winfo_width(), self.minature_frame.winfo_height()), Image.NEAREST)
        image2 = ImageTk.PhotoImage(image)
        self.minature_label = tk.Label(self.minature_frame, image=image2, bg='orange')
        self.minature_label.im = image2
        self.minature_label.grid(row=0, column=0, sticky='news')

    def prepare_main_manu(self):
        self.movie_name_label = tk.Label(self.menu_frame, textvariable=self.__video_name, font=20,
                                         bg=PURPLE, fg='black')
        self.movie_name_label.grid(row=0, column=0, sticky='news')

        self.pixelate_frame = tk.Frame(self.menu_frame, bg=PURPLE)
        self.pixelate_frame.grid(row=1, column=0, sticky='news')
        self.pixelate_frame.grid_propagate(0)
        self.pixelate_frame.rowconfigure(0, weight=1)
        self.pixelate_frame.columnconfigure(0, weight=3)
        self.pixelate_frame.columnconfigure(1, weight=1)

        choices = ['10', '15', '20', '25', '30', '35', '40']
        fnt = tkFont.Font(family='Helvetica', size=14)
        self.pixelate_option_menu = tk.OptionMenu(self.pixelate_frame, self.__pixelate_choice, *choices)
        self.pixelate_option_menu.configure(font=20, bg=PURPLE, fg='black', highlightcolor=PURPLE,
                                            activebackground=PURPLE, relief=tk.GROOVE)
        menu = self.pixelate_frame.nametowidget(self.pixelate_option_menu.menuname)
        menu.config(font=fnt, bg=PURPLE, relief=tk.GROOVE)
        self.pixelate_option_menu['menu'].config(fg='black')
        self.pixelate_option_menu.grid(row=0, column=1, sticky='news')

        self.pixelate_label = tk.Label(self.pixelate_frame, text='pixelate', font=20, bg=GRAY, fg='black')
        self.pixelate_label.grid(row=0, column=0, sticky='news')

        self.check_loop = tk.Checkbutton(self.menu_frame, variable=self.__is_looped, font=20, text='loop',
                                         bg=GRAY, fg='black', highlightcolor='#9966cc',
                                         activebackground='#cc99ff', anchor='w', padx=20)
        self.check_loop.grid(row=2, column=0, sticky='news')

        self.check_right = tk.Checkbutton(self.menu_frame, variable=self.__rotate_right, font=20, text='rotate right',
                                         bg=GRAY, fg='black', highlightcolor='#9966cc',
                                         activebackground='#cc99ff', anchor='w', padx=20, command=lambda: self.check_left.deselect())
        self.check_right.grid(row=3, column=0, sticky='news')

        self.check_left = tk.Checkbutton(self.menu_frame, variable=self.__rotate_left, font=20, text='rotate left',
                                          bg=GRAY, fg='black', highlightcolor='#9966cc',
                                          activebackground='#cc99ff', anchor='w', padx=20, command=lambda: self.check_right.deselect())
        self.check_left.grid(row=4, column=0, sticky='news')

        self.check_inverse_colours = tk.Checkbutton(self.menu_frame, variable=self.__inverse_colours, font=20, text='inverse colours',
                                         bg=GRAY, fg='black', highlightcolor='#9966cc',
                                         activebackground='#cc99ff', anchor='w', padx=20)
        self.check_inverse_colours.grid(row=5, column=0, sticky='news')

        self.play_button = tk.Button(self.menu_frame, text='PLAY', font=20, bg=PURPLE, relief=tk.GROOVE,
                                     highlightcolor=LILA, activebackground=SOMBRA_PURPLE)
        self.play_button.grid(row=6, column=0, sticky='news')

    def prepare_loading_bar(self):
        self.bar_parts = [tk.Frame(self.loading_bar_frame, bg='black') for _ in range(10)]
        for n in range(10):
            self.bar_parts[n].grid(row=0, column=n, sticky='news')

    # --- actions ------------------------
    def open_file(self):
        filename = askopenfilename(initialdir=os.getcwd(), title='Select data file',
                                   filetypes=(('video files', '.mp4'),))
        if filename == "":
            return
        self.__video_path.set(filename)
        self.__video_name.set(self.__video_path.get().split('/')[-1])
        self.__config['video path'] = filename
        save_config(self.__config)
        self.prepare_minature()

    def load_from_pickle(self):
        self.__ascii_frames, path = load_list()
        self.__list_loaded.set(1)
        self.prepare_sandard_minature()
        self.__video_path.set(path)
        self.__video_name.set(self.__video_path.get().split('/')[-1])


class AsciiMoviePlayer(tk.Toplevel):
    def __init__(self, master, **kw):
        tk.Toplevel.__init__(self, master, **kw)
        self.display_frame = tk.Frame(self)




