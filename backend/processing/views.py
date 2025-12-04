import io
import zipfile
import numpy as np
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import cv2
import matplotlib.pyplot as plt
from django.http import JsonResponse
from .models import *
from django.core.files.base import ContentFile


def fig_to_bytes(fig):
    """Convert matplotlib figure to PNG bytes."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()

def img_to_bytes(img_array):
    """Convert numpy image to PNG bytes."""
    buf = io.BytesIO()
    Image.fromarray(img_array).save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()

@csrf_exempt
def upload_image(request):
    if request.method != "POST":
        return HttpResponse("POST required", status=405)

    # Read image
    if request.FILES:
        image_bytes = request.FILES["file"].read()
    else:
        image_bytes = request.body

    pil_img = Image.open(io.BytesIO(image_bytes))

    # --- Save raw image in MongoDB ---
    img_bytes = io.BytesIO()
    pil_img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    rawimage = RawImages(name="uploaded_image")
    rawimage.image.put(img_bytes, content_type="image/png")
    rawimage.save()
    arr = np.array(pil_img)

    # ------ GRAYSCALE ------
    gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)

    # ------ SCATTER ------
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
    plt.colorbar(sc)

    # ------ HISTOGRAM ------
    x_hist = np.sum(gray, axis=0)
    y_hist = np.sum(gray, axis=1)
    fig_hist, (hx, hy) = plt.subplots(1, 2, figsize=(8,4))
    hx.plot(x_hist)
    hy.plot(y_hist)

    # ------ BAR GRAPH ------
    fig_bar, (bx, by) = plt.subplots(1, 2, figsize=(8,4))
    bx.bar(range(len(x_hist)), x_hist)
    by.bar(range(len(y_hist)), y_hist)

    # ------ LINE GRAPH ------
    fig_line, (lx, ly) = plt.subplots(1, 2, figsize=(8,4))
    lx.plot(x_hist)
    ly.plot(y_hist)

    # ------ CREATE ZIP ------
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr("gray.png", img_to_bytes(gray))
        zip_file.writestr("scatter.png", fig_to_bytes(fig_scatter))
        zip_file.writestr("histogram.png", fig_to_bytes(fig_hist))
        zip_file.writestr("bar.png", fig_to_bytes(fig_bar))
        zip_file.writestr("line.png", fig_to_bytes(fig_line))

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type="application/zip")
    response["Content-Disposition"] = "attachment; filename=plots.zip"
    return response

def test(request):
    book = Book(title="Django with MongoDB", author="Avinash")
    book.save()
    return JsonResponse({"message": "Hello World from Django backend!"})

def list_raw_images(request):
    """
    Reads all images from RawImages (MongoDB GridFS) 
    and returns a ZIP containing all images.
    """
    images = RawImages.objects()
    
    # Create an in-memory zip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for img in images:
            if img.image:  # make sure image exists
                # Read image bytes
                file_data = img.image.read()
                # Use filename or fallback to id.png
                filename = img.image.filename or f"{img.id}.png"
                zip_file.writestr(filename, file_data)
    
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="all_raw_images.zip"'
    return response