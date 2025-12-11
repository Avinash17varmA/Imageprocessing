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

def save_image_if_new(pil_img, name="uploaded_image"):
    """
    Saves the image to MongoDB only if it does not already exist.
    Calculates MD5 based on the converted PNG bytes to ensure consistency.
    Returns the RawImages object.
    """
    print("LOG: save_image_if_new called")
    img_bytes = io.BytesIO()
    pil_img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    file_content = img_bytes.getvalue()
    
    img_hash = calculate_md5(file_content)
    print(f"LOG: Calculated hash: {img_hash}")

    duplicate = RawImages.objects(md5=img_hash).first()
    if duplicate:
        print("LOG: Duplicate image found in DB.")
        return duplicate

    # Ensure name ends with .png since we converted it
    if not name.lower().endswith('.png'):
        base_name = name.rsplit('.', 1)[0] if '.' in name else name
        name = f"{base_name}.png"

    print(f"LOG: Saving new raw image to DB: {name}")
    rawimage = RawImages(name=name, md5=img_hash)
    rawimage.image.put(img_bytes, filename=name, content_type="image/png")
    rawimage.save()
    return rawimage

def generate_plots_bytes(pil_img):
    """Generates all plots and returns a dictionary of plot bytes"""
    print("LOG: generate_plots_bytes started")
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
    # Fix: PIL stores images as RGB, so convert RGB to GRAY
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

    # Scatter plot
    print("LOG: Generating Scatter plot")
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

    # Histogram (Standard Intensity Histogram)
    print("LOG: Generating Histogram")
    fig_hist, ax_hist = plt.subplots(figsize=(8, 4))
    ax_hist.hist(gray.ravel(), 256, [0, 256], color='black', alpha=0.7)
    ax_hist.set_title('Pixel Intensity Histogram')
    ax_hist.set_xlabel('Pixel Value')
    ax_hist.set_ylabel('Frequency')
    ax_hist.grid(axis='y', alpha=0.5)

    # Projections (Sum of pixel values along axes)
    print("LOG: Calculating Projections")
    x_proj = np.sum(gray, axis=0)
    y_proj = np.sum(gray, axis=1)

    # Bar graph (using projections)
    print("LOG: Generating Bar graph")
    fig_bar, (bx, by) = plt.subplots(1, 2, figsize=(8,4))
    bx.bar(range(len(x_proj)), x_proj, color='gray')
    bx.set_title('X-Axis Projection')
    by.bar(range(len(y_proj)), y_proj, color='gray')
    by.set_title('Y-Axis Projection')

    # Line graph (using projections)
    print("LOG: Generating Line graph")
    fig_line, (lx, ly) = plt.subplots(1, 2, figsize=(8,4))
    lx.plot(x_proj, color='black')
    lx.set_title('X-Axis Projection')
    ly.plot(y_proj, color='black')
    ly.set_title('Y-Axis Projection')

    print("LOG: All plots generated")
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