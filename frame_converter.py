from PIL import Image, ImageOps
import cv2
import numpy as np
import os
from tkinter import StringVar

# ASCII chars used
ASCII = ['  ', '..', '<<', 'cc', '77', '33', 'xx', 'ee', 'kk', '##', '■■']


class FrameConverter:
    def __init__(self, parent, pixel_size, rotate_right, rotate_left, is_inversed, colour, height, width):
        self.__parent = parent
        self.__pixel_size = pixel_size
        self.__colour = StringVar(parent, colour)
        self.__rotate_left = rotate_left
        self.__rotate_right = rotate_right
        self.__is_inversed = is_inversed
        self.__height = height
        self.__width = width

    # A method that converts pixelated frames into ASCII characters
    def convert(self, path: str):
        # Check if the file exists or if it is an mp4 file.
        if not os.path.exists(path):
            return
        if not path.endswith('.mp4'):
            return

        video = cv2.VideoCapture(path)
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        counter = 0
        success = 1
        frames = []
        length = 0
        height = 0
        while success:
            if self.__parent.force_cancel.get() == 1:
                return [], 0, 0, 0, 0, 0
            success, image = video.read()
            if success:
                # cv2 uses different images coding than PIL thus cvtColor
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image_pil = Image.fromarray(image).resize((self.__height, self.__width), Image.NEAREST)
                length, height = image_pil.size[0], image_pil.size[1]
                pixelated = self.pixelate(image_pil)
                frames.append(pixelated)
                counter += 1
                lb = int(counter * len(self.__parent.bar_parts) / frame_count)
                if counter % int(frame_count/len(self.__parent.bar_parts)) if int(frame_count/len(self.__parent.bar_parts)) != 0 else 1 == 0:
                    for n in range(min(lb, len(self.__parent.bar_parts))):
                        self.__parent.update()
                        self.__parent.bar_parts[n].config(bg=self.__colour.get())
        for fr in self.__parent.bar_parts:
            self.__parent.update()
            fr.config(bg=self.__colour.get())
        return frames, duration, frame_count, fps, length, height

    # A method that converts PIL Image into ASCII characters
    def pixelate(self, image):
        image = image.resize((image.size[0] // self.__pixel_size, image.size[1] // self.__pixel_size), Image.NEAREST)
        # Convert images to black'n'white
        image = image.convert('L')
        if self.__rotate_left:
            image = image.rotate(90)
        elif self.__rotate_right:
            image = image.rotate(270)
        if self.__is_inversed:
            image = ImageOps.invert(image)
        ar = np.asarray(image)
        length = np.shape(ar)[0] - 1
        height = np.shape(ar)[1] - 1
        out = ''
        for i in range(length):
            for j in range(height):
                out += ASCII[ar[i][j] // 25]
            out += '\n'
        return out

