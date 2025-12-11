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
            print("LOG: Request method is not POST")
            return JsonResponse({"error": "POST method required"}, status=405)

        # --- Read image: Only from request.FILES ---
        print("LOG: processing upload_image request")
        if "file" not in request.FILES:
            print("LOG: No file in request.FILES")
            return JsonResponse({"error": "No file uploaded"}, status=400)

        uploaded_file = request.FILES["file"]
        print(f"LOG: Received file: {uploaded_file.name}")
        image_bytes = uploaded_file.read()

        if not image_bytes:
            print("LOG: Empty file uploaded")
            return JsonResponse({"error": "Empty file uploaded"}, status=400)

        # --- Open image ---
        print("LOG: Opening image with PIL")
        pil_img = Image.open(io.BytesIO(image_bytes))

        # --- Save raw image if new ---
        # We use the filename from the upload if available
        name = uploaded_file.name if uploaded_file.name else "uploaded_image"
        print(f"LOG: Saving/Checking raw image: {name}")
        raw_image_obj = save_image_if_new(pil_img, name=name)
        print(f"LOG: Raw image object ID: {raw_image_obj.id}")

        # --- Check if processed images already exist ---
        print("LOG: Checking for existing processed images")
        plots = get_processed_images_from_db(raw_image_obj)

        if plots is None:
            # generate new processed images
            print("LOG: No existing plots found. Generating new plots...")
            plots = generate_plots_bytes(pil_img)
            print("LOG: Plots generated. Saving to DB...")

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
            print("LOG: Processed images saved to DB")
        else:
            print("LOG: Found existing plots in DB. Using them.")

        # --- Create ZIP ---
        print("LOG: Creating ZIP file response")
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for key, value in plots.items():
                zip_file.writestr(f"{key}.png", value)

        zip_buffer.seek(0)
        print("LOG: ZIP ready. Sending response.")

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
        used_names = set()
        for img in images:
            if img.image:  # make sure image exists
                # Read image bytes
                file_data = img.image.read()
                
                # Use stored name or fallback
                filename = img.name if img.name else (img.image.filename or f"{img.id}.png")
                
                # Ensure unique filename in zip
                while filename in used_names:
                    if '.' in filename:
                        name_part, ext = filename.rsplit('.', 1)
                        filename = f"{name_part}_1.{ext}"
                    else:
                        filename = f"{filename}_1"
                
                used_names.add(filename)
                zip_file.writestr(filename, file_data)
    
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="all_raw_images.zip"'
    return response