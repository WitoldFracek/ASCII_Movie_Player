from PIL import Image, ImageOps
import cv2
import numpy as np
import os
import time

ASCII = ['  ', '..', '<<', 'cc', '77', '33', 'xx', 'ee', 'kk', '##', '⣿⣿']
SOMBRA_PURPLE = '#a350f9'


def convert(path: str, pixel_size, rotate_right, rotate_left, is_inversed, parent):
    if not os.path.exists(path):
        return
    if not path.endswith('.mp4'):
        return

    # --- BEGIN ------
    video = cv2.VideoCapture(path)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    counter = 0
    success = 1
    frames = []
    length = 0
    width = 0
    parent.update()
    while success:
        success, image = video.read()
        if success:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(image)
            pixelated, length, width = pixelate(image_pil, pixel_size, rotate_left, rotate_right, is_inversed)
            frames.append(pixelated)
            counter += 1
            lb = int(counter * len(parent.bar_parts) / frame_count)
            if counter % int(frame_count/len(parent.bar_parts)) if int(frame_count/len(parent.bar_parts)) != 0 else 1 == 0:
                for n in range(min(lb, len(parent.bar_parts))):
                    parent.update()
                    parent.bar_parts[n].config(bg=SOMBRA_PURPLE)
    for fr in parent.bar_parts:
        parent.update()
        fr.config(bg=SOMBRA_PURPLE)
    return frames, duration, frame_count, fps, length, width


def pixelate(image, pixel_size, rotate_left, rotate_right, is_inversed):
    image = image.resize((image.size[0] // pixel_size, image.size[1] // pixel_size), Image.NEAREST)
    image = image.convert('L')
    if rotate_left:
        image = image.rotate(90)
    elif rotate_right:
        image = image.rotate(270)
    if is_inversed:
        image = ImageOps.invert(image)
    ar = np.asarray(image)
    length = np.shape(ar)[0] - 1
    width = np.shape(ar)[1] - 1
    out = ''
    for i in range(length):
        for j in range(width):
            out += ASCII[ar[i][j] // 25]
        out += '\n'
    return out, length, width

