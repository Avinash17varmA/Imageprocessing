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
from .functions import *

@csrf_exempt
def upload_image(request):
    try:
        if request.method != "POST":
            return JsonResponse({"error": "POST method required"}, status=405)

        # --- Read image: Only from request.FILES ---
        if "file" not in request.FILES:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        uploaded_file = request.FILES["file"]
        image_bytes = uploaded_file.read()

        if not image_bytes:
            return JsonResponse({"error": "Empty file uploaded"}, status=400)

        # --- Open image ---
        pil_img = Image.open(io.BytesIO(image_bytes))

        # --- MD5 & Save raw image if new ---
        img_hash = calculate_md5(image_bytes)
        save_image_if_new(pil_img, img_hash)
        raw_image_obj = RawImages.objects(md5=img_hash).first()

        # --- Check if processed images already exist ---
        plots = get_processed_images_from_db(raw_image_obj)

        if plots is None:
            # generate new processed images
            plots = generate_plots_bytes(pil_img)

            processed = ProcessedImages(
                name="processed_" + (raw_image_obj.name or "image"),
                original_image=raw_image_obj
            )

            for key, value in plots.items():
                getattr(processed, key).put(
                    io.BytesIO(value),
                    content_type="image/png"
                )
            processed.save()

        # --- Create ZIP ---
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for key, value in plots.items():
                zip_file.writestr(f"{key}.png", value)

        zip_buffer.seek(0)

        return HttpResponse(
            zip_buffer,
            content_type="application/zip",
            headers={
                "Content-Disposition": 'attachment; filename="plots.zip"'
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


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