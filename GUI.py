from PIL import Image, ImageTk
import cv2
import numpy as np
from time import sleep
import tkinter as tk
from tkinter import font as tkFont
import json
import random
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
import pickle as rick
import os
import frame_converter as fc

# D:/HDD/programowanie_python/DiscordBots/PicturesBot/bad_apple/bad_apple.mp4

#constants
LOADING_BAR_FRACTIONS = 100
ASCII = ['  ', '..', '<<', 'cc', '77', '33', 'xx', 'ee', 'kk', '##', '⣿⣿']
CONFIG = '.\\ascii_movie_config.json'
SOMBRA_PURPLE = '#a350f9'
#HELV_20 = tkFont.Font(family='Helvetica', size=20)
#HELV_14 = tkFont.Font(family='Helvetica', size=14)


def prepare_config():
    if os.path.exists(CONFIG):
        conf: dict = get_config()
        right = ['height', 'length', 'video path', 'cover photo', 'logo', 'error', 'main colour', 'light colour',
                 'foreground colour', 'is looped', 'rotate left', 'rotate right', 'invert colours']
        for key in conf:
            if key not in right:
                create_config()
                return
    else:
        create_config()


def create_config():
    conf = {
            'height': 500,
            'length': 1000,
            "video path": "",
            "cover photo": "./ASCII_movies.png",
            "logo": "./ASCII_logo.png",
            "error": "./ASCII_ERROR.png",
            "main colour": "#ff6600",
            "light colour": "#ff9900",
            "foreground colour": "black",
            "is looped": False,
            "rotate left": False,
            "rotate right": False,
            "invert colours": False
            }
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


def get_quarter_frame(path: str):
    if not os.path.exists(path):
        return None
    if not path.endswith('.mp4'):
        return None
    video = cv2.VideoCapture(path)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    index = max(2, int(frame_count/4))
    video.set(cv2.CAP_PROP_POS_FRAMES, index - 1)
    success, image = video.read()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    im_pil = Image.fromarray(image)
    return im_pil.convert('L')


class AsciiMovie(tk.Tk):
    def __init__(self, parent=None):
        tk.Tk.__init__(self, parent)

        # --- Configuration ------------------------------
        self.title('ASCII movie player')
        prepare_config()
        self.__config = get_config()
        self.geometry(f'{self.__config["length"]}x{self.__config["height"]}')
        self.iconphoto(False, tk.PhotoImage(file=self.__config['logo']))
        self.bind('<Control-o>', self.open_file)
        self.bind('<Control-s>', self.load_to_pickle)
        self.bind('<Control-l>', self.load_from_pickle)

        # --- Colours ------------------------------------
        self.MAIN_COLOUR = self.__config['main colour']
        self.LIGHT_MAIN_COLOUR = self.__config['light colour']
        self.MAIN_FG = self.__config['foreground colour']

        self.__colours = {
            'RED': ('red', '#ff3333', 'black'),
            'ORANGE': ('#ff6600', '#ff9900', 'black'),
            'YELLOW': ('#ffcc00', '#ffcc33', 'black'),
            'LIME': ('#99ff00', '#ccff66', 'black'),
            'GREEN': ('#009900', '#339900', 'black'),
            'CYAN': ('#OOFFFF', '#COCOCO', 'black'),
            'BLUE': ('#0033cc', '#0066cc', 'white'),
            'PURPLE': ('#a350f9', '#cc99ff', 'black'),
            'VIOLET': ('#a350f9', '#cc99ff', 'black'),
            'PINK': ('#cc0099', '#ff33ff', 'white'),
            'GRAY': ('#909090', '#b8b8b8', 'black')
        }

        self.FONT = ('Weibei', 14)
        #Arial Narrow, Cooper Black, Comic Sans MS


        # --- variables ----------------------------------
        self.__video_path = tk.StringVar()
        self.__video_path.set(self.__config['video path'])
        self.__video_name = tk.StringVar()
        self.__video_name.set(self.__video_path.get().split('/')[-1])
        self.__video_pickle_path = tk.StringVar(self, "")
        self.__is_looped = tk.IntVar()
        self.__is_looped.set(0)
        self.__rotate_right = tk.IntVar()
        self.__rotate_right.set(0)
        self.__rotate_left = tk.IntVar()
        self.__rotate_left.set(0)
        self.__invert_colours = tk.IntVar(self, 0)
        self.__pixelate_choice = tk.StringVar()
        self.__pixelate_choice.set('20')
        self.__ascii_frames = []
        self.__converted_movie_length = 0
        self.__converted_movie_height = 0
        self.__converted_movie_px_length = 0
        self.__converted_movie_px_height = 0
        self.__converted_movie_duration = 0
        self.__converted_movie_fps = 0
        self.__converted_movie_frame_count = 0
        self.__list_loaded = tk.IntVar(self, 0)
        self.__convert_button_text = tk.StringVar(self, "CONVERT")
        self.force_cancel = tk.IntVar(self, 0)

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
        self.menu_frame = tk.Frame(self, bg='black')
        self.menu_frame.grid(row=0, column=0, sticky='news')
        self.menu_frame.columnconfigure(0, weight=1)
        self.menu_frame.rowconfigure(0, weight=2)
        self.menu_frame.rowconfigure(1, weight=1)
        self.menu_frame.rowconfigure(2, weight=1)
        self.menu_frame.rowconfigure(3, weight=1)
        self.menu_frame.rowconfigure(4, weight=1)
        self.menu_frame.rowconfigure(5, weight=1)
        self.menu_frame.rowconfigure(6, weight=1)
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
        for n in range(LOADING_BAR_FRACTIONS):
            self.loading_bar_frame.columnconfigure(n, weight=1)

    def prepare_file_menu_bar(self):
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)
        self.menu_bar.add_cascade(label='File', menu=self.prepare_file_menu_cascade(self.menu_bar))
        self.menu_bar.add_cascade(label='Themes', menu=self.prepare_colour_cascade(self.menu_bar))

    def prepare_file_menu_cascade(self, parent_menu):
        self.file_menu = tk.Menu(parent_menu)
        self.file_menu.add_command(label='Open mp4 (ctrl+O)', command=self.open_file)
        self.file_menu.add_command(label='Save (ctrl+S)', command=self.load_to_pickle)
        self.file_menu.add_command(label='Load (ctrl+L)', command=self.load_from_pickle)
        if not self.__ascii_frames:
            self.file_menu.entryconfig('Save (ctrl+S)', state='disabled')
        return self.file_menu

    def prepare_colour_cascade(self, parent_menu):
        self.colour_menu = tk.Menu(parent_menu)
        for key in self.__colours:
            self.colour_menu.add_command(label=key.lower(), command=lambda: self.set_colour_theme(self.__colours[key]))
        return self.colour_menu

    def set_colour_theme(self, colour):
        self.MAIN_COLOUR = colour[0]
        self.LIGHT_MAIN_COLOUR = colour[1]
        self.MAIN_BG = colour[2]
        self.update_colours()

    def update_colours(self):
        pass

    def prepare_minature(self):
        if self.__video_path.get() == "":
            self.prepare_sandard_minature()
        else:
            self.prepare_custom_minature()

    def prepare_sandard_minature(self):
        self.minature_frame.update()
        if not os.path.exists(self.__config['cover photo']):
            self.prepare_error_minature()
            return
        else:
            image_png = Image.open(self.__config['cover photo']).resize((self.minature_frame.winfo_width(),
                                                                         self.minature_frame.winfo_height()))
            image2 = ImageTk.PhotoImage(image_png)
            image_png.close()
        self.minature_label = tk.Label(self.minature_frame, image=image2, bg='black')
        self.minature_label.im = image2
        self.minature_label.grid(row=0, column=0, sticky='news')

    def prepare_error_minature(self):
        self.minature_frame.update()
        if not os.path.exists(self.__config['error']):
            messagebox.showerror('DAMAGED CONFIGURATION FILE', 'Configuration file is damaged.')
            return
        else:
            image_png = Image.open(self.__config['cover photo']).resize((self.minature_frame.winfo_width(),
                                                                         self.minature_frame.winfo_height()))
            image2 = ImageTk.PhotoImage(image_png)
            image_png.close()
        self.minature_label = tk.Label(self.minature_frame, image=image2, bg='black')
        self.minature_label.im = image2
        self.minature_label.grid(row=0, column=0, sticky='news')

    def prepare_custom_minature(self):
        self.minature_frame.update()
        if not os.path.exists(self.__config['video path']):
            self.prepare_error_minature()
            return
        image = get_quarter_frame(self.__config['video path'])
        if image is None:
            self.prepare_sandard_minature()
            return
        image = image.resize((self.minature_frame.winfo_width(), self.minature_frame.winfo_height()), Image.NEAREST)
        image2 = ImageTk.PhotoImage(image)
        self.minature_label = tk.Label(self.minature_frame, image=image2, bg='black')
        self.minature_label.im = image2
        self.minature_label.grid(row=0, column=0, sticky='news')

    def prepare_main_manu(self):
        self.movie_name_label = tk.Label(self.menu_frame, textvariable=self.__video_name, font=self.FONT,
                                         bg='black', fg='white')
        self.movie_name_label.grid(row=0, column=0, sticky='news')

        self.pixelate_frame = tk.Frame(self.menu_frame, bg='white')
        self.pixelate_frame.grid(row=1, column=0, sticky='news')
        self.pixelate_frame.grid_propagate(0)
        self.pixelate_frame.rowconfigure(0, weight=1)
        self.pixelate_frame.columnconfigure(0, weight=3)
        self.pixelate_frame.columnconfigure(1, weight=1)

        choices = ['10', '15', '20', '25', '30', '35', '40']
        fnt = tkFont.Font(family='Consolas', size=14)
        self.pixelate_option_menu = tk.OptionMenu(self.pixelate_frame, self.__pixelate_choice, *choices,
                                                  command=self.parameter_change_convertoin)
        self.pixelate_option_menu.configure(font=self.FONT, bg='white', fg='black', highlightcolor=self.LIGHT_MAIN_COLOUR,
                                            activebackground=self.LIGHT_MAIN_COLOUR, relief=tk.GROOVE)
        menu = self.pixelate_frame.nametowidget(self.pixelate_option_menu.menuname)
        menu.config(font=fnt, bg='white', relief=tk.GROOVE)
        self.pixelate_option_menu['menu'].config(fg='black')
        self.pixelate_option_menu.grid(row=0, column=1, sticky='news')

        self.pixelate_label = tk.Label(self.pixelate_frame, text='PIXELATE', font=self.FONT, bg='white', fg='black')
        self.pixelate_label.grid(row=0, column=0, sticky='news')

        self.check_loop = tk.Checkbutton(self.menu_frame, variable=self.__is_looped, font=self.FONT, text='LOOP',
                                         bg='white', fg='black', highlightcolor=self.LIGHT_MAIN_COLOUR,
                                         activebackground=self.LIGHT_MAIN_COLOUR, anchor='w', padx=20, relief=tk.GROOVE)
        self.check_loop.grid(row=2, column=0, sticky='news')

        self.check_right = tk.Checkbutton(self.menu_frame, variable=self.__rotate_right, font=self.FONT, text='ROTATE RIGHT',
                                         bg='white', fg='black', highlightcolor=self.LIGHT_MAIN_COLOUR,
                                         activebackground=self.LIGHT_MAIN_COLOUR, anchor='w', padx=20,
                                         command=self.deselect_left, relief=tk.GROOVE)
        self.check_right.grid(row=3, column=0, sticky='news')

        self.check_left = tk.Checkbutton(self.menu_frame, variable=self.__rotate_left, font=self.FONT, text='ROTATE LEFT',
                                         bg='white', fg='black', highlightcolor=self.LIGHT_MAIN_COLOUR,
                                         activebackground=self.LIGHT_MAIN_COLOUR, anchor='w', padx=20, command=self.deselect_right,
                                         relief=tk.GROOVE)
        self.check_left.grid(row=4, column=0, sticky='news')

        self.check_inverse_colours = tk.Checkbutton(self.menu_frame, variable=self.__invert_colours, font=self.FONT,
                                                    text='INVERT COLOURS',
                                                    bg='white', fg='black', highlightcolor=self.LIGHT_MAIN_COLOUR,
                                                    activebackground=self.LIGHT_MAIN_COLOUR, anchor='w', padx=20,
                                                    command=self.parameter_change_convertoin, relief=tk.GROOVE)
        self.check_inverse_colours.grid(row=5, column=0, sticky='news')

        self.play_button = tk.Button(self.menu_frame, textvariable=self.__convert_button_text, font=self.FONT,
                                     bg='black', fg='white',
                                     relief=tk.GROOVE, highlightcolor=self.LIGHT_MAIN_COLOUR,
                                     activebackground=self.LIGHT_MAIN_COLOUR,
                                     command=self.decide_main_button_action)
        self.play_button.grid(row=6, column=0, sticky='news')

    def prepare_loading_bar(self):
        self.bar_parts = [tk.Frame(self.loading_bar_frame, bg='black') for _ in range(LOADING_BAR_FRACTIONS)]
        for n in range(LOADING_BAR_FRACTIONS):
            self.bar_parts[n].grid(row=0, column=n, sticky='news')

    # FILE MANAGEMENT
    # Specify the path to an mp4 file.
    def open_file(self, e=None):
        filename = askopenfilename(initialdir=os.getcwd(), title='Select data file',
                                   filetypes=(('video files', '.mp4'),))
        if filename == "":
            return
        self.__ascii_frames = []
        self.file_menu.entryconfig('Save (ctrl+S)', state='disabled')
        self.__video_path.set(filename)
        self.__video_name.set(self.__video_path.get().split('/')[-1])
        self.__config['video path'] = filename
        save_config(self.__config)
        self.__list_loaded.set(0)
        self.__video_pickle_path.set("")
        self.prepare_minature()
        self.__convert_button_text.set('CONVERT')

    # Loads converted ASCII frames to a pickle file.
    # The 'amc' extension is used to force dedicated for ASCII Movie Converter program files to open.
    def load_to_pickle(self, e=None):
        if not self.__ascii_frames:
            messagebox.showerror(title='ERROR', message='No frames converted')
            return
        file_path: str = asksaveasfilename(initialdir=os.getcwd(), title='Select saving location',
                                           filetypes=(('ASCII Movie Converter files', '.amc'),))
        if file_path == "":
            return
        if not file_path.endswith('.amc'):
            file_path += '.amc'
        with open(file_path, 'wb') as file:
            rick.dump(self.__ascii_frames, file)
            rick.dump(self.__converted_movie_duration, file)
            rick.dump(self.__converted_movie_frame_count, file)
            rick.dump(self.__converted_movie_fps, file)
            rick.dump(self.__converted_movie_length, file)
            rick.dump(self.__converted_movie_height, file)
            rick.dump(self.__converted_movie_px_length, file)
            rick.dump(self.__converted_movie_px_height, file)

    # Loads converted ASCII frames from a pickle file.
    def load_from_pickle(self, e=None):
        path = askopenfilename(initialdir=os.getcwd(), title='Select saved frames',
                               filetypes=(('ASCII Movie Converter files', '.amc'),))
        with open(path, 'rb') as file:
            try:
                self.__ascii_frames = rick.load(file)
                self.__converted_movie_duration = rick.load(file)
                self.__converted_movie_frame_count = rick.load(file)
                self.__converted_movie_fps = rick.load(file)
                self.__converted_movie_length = rick.load(file)
                self.__converted_movie_height = rick.load(file)
                self.__converted_movie_px_length = rick.load(file)
                self.__converted_movie_px_height = rick.load(file)
            except EOFError:
                messagebox.showerror('WARNING', 'Selected file is corrupted. Select a different file')
                return
            except TypeError:
                messagebox.showerror('WARNING', 'Selected file is corrupted. Select a different file')
                return
        self.__list_loaded.set(1)
        self.prepare_sandard_minature()
        self.__video_pickle_path.set(path)
        self.__video_path.set("")
        self.__video_name.set(self.__video_pickle_path.get().split('/')[-1])
        self.file_menu.entryconfig('Save (ctrl+S)', state='normal')
        self.__convert_button_text.set('PLAY')

    # PLAYER ACTIONS
    # Decides whether the video is to be converted or can be played from loaded list.
    def decide_main_button_action(self):
        self.clear_loading_bar()
        if self.__convert_button_text.get() == 'CONVERT':
            self.force_cancel.set(0)
            self.__convert_button_text.set('CANCEL')
            self.convert_movie_from_file()
        elif self.__convert_button_text.get() == 'PLAY':
            self.play_video()
        elif self.__convert_button_text.get() == 'CANCEL':
            self.force_cancel.set(1)
            self.__convert_button_text.set('CONVERT')
            self.file_menu.entryconfig('Save (ctrl+S)', state='disabled')

    def clear_menu_options(self):
        self.check_left.deselect()
        self.check_right.deselect()
        self.check_loop.deselect()
        self.check_inverse_colours.deselect()

    def clear_loading_bar(self):
        for fr in self.bar_parts:
            fr.config(bg='black')

    def parameter_change_convertoin(self, e=None):
        self.force_cancel.set(1)
        self.__convert_button_text.set('CONVERT')
        self.after(1000, self.force_cancel.set, 0)

    def deselect_left(self, e=None):
        self.check_left.deselect()
        self.parameter_change_convertoin()

    def deselect_right(self, e=None):
        self.check_right.deselect()
        self.parameter_change_convertoin()

    # Prepares frames list with additional information such as duration, frame count etc.
    def convert_movie_from_file(self):
        rot_left = True if self.__rotate_left.get() > 0 else False
        rot_right = True if self.__rotate_right.get() > 0 else False
        is_inverted = True if self.__invert_colours.get() > 0 else False
        ret, duration, frame_count, fps, length, height, px_length, px_height = fc.convert(self.__video_path.get(),
                                                                                           int(self.__pixelate_choice.get()),
                                                                                           rot_right, rot_left,
                                                                                           is_inverted, self,
                                                                                           self.MAIN_COLOUR)
        self.__ascii_frames = ret
        self.__converted_movie_duration = duration
        self.__converted_movie_frame_count = frame_count
        self.__converted_movie_fps = fps
        self.__converted_movie_length = length
        self.__converted_movie_height = height
        self.__converted_movie_px_length = px_length
        self.__converted_movie_px_height = px_height

        if self.force_cancel.get() == 0:
            self.__convert_button_text.set('PLAY')
            self.file_menu.entryconfig('Save (ctrl+S)', state='normal')

    # Creates an AsciiMoviePlayer window
    def play_video(self):
        apk = AsciiMoviePlayer(self,
                               self.__ascii_frames,
                               self.__converted_movie_duration,
                               self.__converted_movie_frame_count,
                               self.__converted_movie_length,
                               self.__converted_movie_height,
                               self.__converted_movie_px_length,
                               self.__converted_movie_px_height,
                               self.__is_looped,
                               self.__config['logo'],
                               self.MAIN_COLOUR,
                               self.LIGHT_MAIN_COLOUR,
                               self.MAIN_FG)
        apk.grab_set()
        for fr in self.bar_parts:
            fr.config(bg='black')


class AsciiMoviePlayer(tk.Toplevel):
    def __init__(self, master: AsciiMovie, frame_list, duration, frame_count, length, height, px_l, px_h, is_looped,
                 logo_path, main_colour, light_colour, fg_colour, **kw):
        tk.Toplevel.__init__(self, master, **kw)
        self.grab_set()

        # --- Layout configuration -------------------------
        self.iconphoto(False, tk.PhotoImage(file=logo_path))
        self.geometry(f'{length}x{height}')
        self.resizable(True, True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.display_frame = tk.Frame(self, bg='black')
        self.display_frame.rowconfigure(0, weight=100)
        self.display_frame.rowconfigure(1, weight=1)
        self.display_frame.rowconfigure(2, weight=1)
        self.display_frame.columnconfigure(0, weight=1)
        self.display_frame.columnconfigure(1, weight=4)
        self.display_frame.grid(row=0, column=0, sticky='news')

        # --- Fields configuration ----------------------------
        self.__ascii_frames = frame_list
        self.__length = length
        self.__height = height
        self.__px_length = px_l
        self.__px_height = px_h
        self.__duration = duration
        self.__frame_count = frame_count
        self.__display_text = tk.StringVar(self, "")
        self.__button_text = tk.StringVar(self, "PLAY")
        self.__is_looped = tk.IntVar(self, is_looped.get())
        self.__current_frame = tk.IntVar(self, 0)
        self.__movie_length = len(frame_list)
        self.__delay = int(self.__duration * 1000 / self.__frame_count)
        self.__is_paused = tk.IntVar(self, 0)
        self.__delta = 0.1

        # --- GUI elements configuration -------------------------------------
        # PLAY/PAUSE BUTTON
        self.play_pause_button = tk.Button(self.display_frame, textvariable=self.__button_text, relief=tk.GROOVE,
                                           bg=main_colour,  highlightcolor=light_colour,
                                           activebackground=light_colour,
                                           command=self.decide_action, fg=fg_colour)
        self.play_pause_button.grid(row=2, column=0, sticky='news')
        self.play_pause_button.grid_propagate(0)

        # FILLING LABEL
        self.empty_label = tk.Label(self.display_frame, bg='black')
        self.empty_label.grid(row=2, column=1, sticky='news')
        self.empty_label.grid_propagate(0)

        # DISPLAY LABEL
        self.display = tk.Label(self.display_frame, bg='black', fg='white', textvariable=self.__display_text,
                                justify='left', font=('Consolas', 10), anchor='center', width=self.__px_length)
        self.display.grid(row=0, column=0, columnspan=2, sticky='news')
        self.display.grid_propagate(0)

        # MOVIE BAR
        self.movie_bar = tk.Scrollbar(self.display_frame, orient=tk.HORIZONTAL, jump=1, width=15,
                                      command=self.rewind)
        self.movie_bar.grid(row=1, column=0, columnspan=2, sticky='news')
        self.movie_bar.grid_propagate(0)

    def rewind(self, *a):
        self.pause_video()
        ratio = float(a[1])
        self.__current_frame.set(int(self.__frame_count * ratio))
        self.movie_bar.set(ratio, ratio+self.__delta)

    def decide_action(self):
        if self.__button_text.get() == 'PLAY':
            self.__button_text.set('PAUSE')
            self.play_video()
        else:
            self.pause_video()

    def play_video(self):
        self.__is_paused.set(0)
        gen = self.frame_generator()
        self.update_label(gen)

    def pause_video(self):
        self.__is_paused.set(1)
        self.__button_text.set('PLAY')

    def frame_generator(self):
        while self.__current_frame.get() < self.__movie_length and self.__is_paused.get() == 0:
            current = self.__current_frame.get()
            yield self.__ascii_frames[current]
            current += 1
            self.__current_frame.set(current)
            if self.__is_looped.get() == 1 and self.__current_frame.get() == self.__movie_length-1:
                self.__current_frame.set(0)
        if self.__is_paused.get() == 0:
            self.__current_frame.set(0)
            self.__is_paused.set(1)
            self.__button_text.set('PLAY')

    def update_label(self, gen):
        try:
            frame = next(gen)
        except StopIteration:
            return
        self.__display_text.set(frame)
        passed = self.__current_frame.get()/self.__frame_count
        self.movie_bar.set(passed, min(1, passed+self.__delta))
        self.display.after(self.__delay, self.update_label, gen)






