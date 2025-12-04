import io
import hashlib
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
from .models import *
# ---------- Helper functions ----------

def calculate_md5(file_bytes):
    """Calculate MD5 hash for a file in bytes"""
    md5 = hashlib.md5()
    md5.update(file_bytes)
    return md5.hexdigest()

def save_image_if_new(pil_img, img_hash, name="uploaded_image"):
    """
    Saves the image to MongoDB only if it does not already exist.
    Returns True if saved, False if duplicate.
    """
    duplicate = RawImages.objects(md5=img_hash).first()
    if duplicate:
        return False

    img_bytes = io.BytesIO()
    pil_img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    rawimage = RawImages(name=name, md5=img_hash)
    rawimage.image.put(img_bytes, content_type="image/png")
    rawimage.save()
    return True

def generate_plots_bytes(pil_img):
    """Generates all plots and returns a dictionary of plot bytes"""
    def img_to_bytes(img):
        buf = io.BytesIO()
        Image.fromarray(img).save(buf, format='PNG')
        buf.seek(0)
        return buf.getvalue()

    def fig_to_bytes(fig):
        buf = io.BytesIO()
        fig.savefig(buf, format='PNG')
        buf.seek(0)
        plt.close(fig)
        return buf.getvalue()

    arr = np.array(pil_img)
    gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)

    # Scatter plot
    h, w = gray.shape
    small = cv2.resize(gray, (int(w * 0.5), int(h * 0.5)))
    xs, ys, intensity = [], [], []
    for y in range(small.shape[0]):
        for x in range(small.shape[1]):
            if small[y, x] != 255:
                xs.append(x)
                ys.append(y)
                intensity.append(small[y, x])
    fig_scatter, ax1 = plt.subplots()
    sc = ax1.scatter(xs, ys, c=intensity, cmap="gray", s=0.5)
    plt.colorbar(sc, ax=ax1)

    # Histogram
    x_hist = np.sum(gray, axis=0)
    y_hist = np.sum(gray, axis=1)
    fig_hist, (hx, hy) = plt.subplots(1, 2, figsize=(8,4))
    hx.plot(x_hist)
    hy.plot(y_hist)

    # Bar graph
    fig_bar, (bx, by) = plt.subplots(1, 2, figsize=(8,4))
    bx.bar(range(len(x_hist)), x_hist)
    by.bar(range(len(y_hist)), y_hist)

    # Line graph
    fig_line, (lx, ly) = plt.subplots(1, 2, figsize=(8,4))
    lx.plot(x_hist)
    ly.plot(y_hist)

    return {
        "grayscale": img_to_bytes(gray),
        "scatter": fig_to_bytes(fig_scatter),
        "histogram": fig_to_bytes(fig_hist),
        "bar": fig_to_bytes(fig_bar),
        "line": fig_to_bytes(fig_line)
    }

def get_processed_images_from_db(raw_image_obj):
    """
    Fetch processed images for a given RawImages object from MongoDB.
    Returns a dictionary of bytes if found, else None.
    """
    processed = ProcessedImages.objects(original_image=raw_image_obj).first()
    if not processed:
        return None

    images_dict = {}
    for key in ["grayscale", "scatter", "histogram", "bar", "line"]:
        file_field = getattr(processed, key)
        if file_field:
            images_dict[key] = file_field.read()  # read bytes from GridFS
    return images_dict