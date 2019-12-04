import cv2
import numpy as np

# -*- coding: utf-8 -*-

def loadImage(img_file):
    img = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)

    if img.shape[0] == 2:
        img = img[0]
    if len(img.shape) == 2: img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    img = np.array(img)
    return img

def adjustImageRatio(img):
    h, w, _ = img.shape
    if w // h >= 8:
        img = cv2.resize(img, (w, 2 * h), interpolation=cv2.INTER_LINEAR)
    elif h // w >= 8:
        img = cv2.resize(img, (w * 2, h), interpolation=cv2.INTER_LINEAR)

    return img

def createImageBorder(img, img_size=1024, color=[255,255,255]):
    h, w, _ = img.shape
    if img_size // 2 > w and img_size // 2 > h:
        l = r = (img_size // 2 - w) // 2
        t = b = (img_size // 2 - h) // 2
    else:
        t = b = l = r = 1
    constant = cv2.copyMakeBorder(img, t, b, l, r, cv2.BORDER_CONSTANT, value=color)
    return constant

def adjustImageBorder(img, img_size=128, color=[255,255,255]):
    h, w, _ = img.shape
    if h > w:
        l = r = (h-w)//2
        t = b = 0
    elif w > h:
        l = r = 0
        t = b = (w-h)//2
    else:
        t = b = l = r = 0
    constant = cv2.copyMakeBorder(img, t, b, l, r, cv2.BORDER_CONSTANT, value=color)
    constant = cv2.copyMakeBorder(constant, h//4, h//4, w//4, w//4, cv2.BORDER_CONSTANT, value=color)
    img = cv2.resize(constant, (img_size, img_size), interpolation=cv2.INTER_CUBIC)
    return img

def cropBBoxOnImage(img, charBBox):
    x_min, y_min = charBBox[0]
    x_max, y_max = charBBox[2]
    x_min, y_min, x_max, y_max = int(round(x_min)), int(round(y_min)), int(round(x_max)), int(round(y_max))
    img = img[y_min:y_max, x_min:x_max, :]
    return img

def normalizeMeanVariance(in_img, mean=(0.485, 0.456, 0.406), variance=(0.229, 0.224, 0.225)):
    img = in_img.copy().astype(np.float32)
    img -= np.array([mean[0] * 255.0, mean[1] * 255.0, mean[2] * 255.0], dtype=np.float32)
    img /= np.array([variance[0] * 255.0, variance[1] * 255.0, variance[2] * 255.0], dtype=np.float32)
    return img

def resize_aspect_ratio(img, user_defined_size, interpolation, mag_ratio=1):
    height, width, channel = img.shape

    mag_org_size = mag_ratio * max(height, width)

    if mag_org_size > user_defined_size: #
        mag_org_size = user_defined_size

    ratio = mag_org_size / max(height, width)
    target_h, target_w = int(height * ratio), int(width * ratio)
    proc = cv2.resize(img, (target_w, target_h), interpolation = interpolation)

    target_h32, target_w32 = target_h, target_w
    if target_h % 32 != 0:
        target_h32 = target_h + (32 - target_h % 32)
    if target_w % 32 != 0:
        target_w32 = target_w + (32 - target_w % 32)

    resized = np.zeros((target_h32, target_w32, channel), dtype=np.float32)
    resized[0:target_h, 0:target_w, :] = proc


    target_h, target_w = target_h32, target_w32
    size_heatmap = (int(target_w/2), int(target_h/2))
    return resized, ratio, size_heatmap


def delNoiseBorderLine(img):
    canvas = np.zeros(img.shape, dtype=img.dtype)
    canvas[img[:, :, 3] == 255] = 255
    kernel = np.ones((3, 3), np.uint8)
    canvas = cv2.erode(canvas, kernel, iterations=4)
    img[canvas == 0] = 255
    if img.shape[2] == 4: img = img[:, :, :3]
    return img

def cvt2HeatmapImg(img):
    img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    img = cv2.applyColorMap(img, cv2.COLORMAP_JET)
    return img
