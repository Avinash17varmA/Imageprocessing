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
from .functions import calculate_md5, save_image_if_new, get_processed_images_from_db, generate_plots_bytes

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

        # --- Calculate Hash for Cache Key ---
        pil_img = Image.open(io.BytesIO(image_bytes))

        # We can use the same hash calculation as save_image_if_new logic or re-do it here.
        # Let's trust functions.calculate_md5
        img_temp_bytes = io.BytesIO()
        pil_img.save(img_temp_bytes, format='PNG')
        img_content_for_hash = img_temp_bytes.getvalue()
        img_hash = calculate_md5(img_content_for_hash)
        
        cache_key = f"processed_plots_{img_hash}"
        print(f"LOG: Checking Redis for key: {cache_key}")
        
        from django.core.cache import cache
        cached_plots = cache.get(cache_key)

        plots = None
        # Define expected keys
        expected_keys = {
            "grayscale", "scatter", "histogram", "bar", "line", 
            "edge_detection", "threshold", "blurred",
            "inverted", "dilated", "eroded", "sharpened"
        }
        
        if cached_plots and all(k in cached_plots for k in expected_keys):
            print("LOG: Valid cache entry found in Redis with all expected plots. Using it.")
            plots = cached_plots
        else:
            if cached_plots:
                print("LOG: Cache entry found but missing some plots. Regenerating...")
            else:
                print("LOG: No cache entry in Redis.")

            # --- Save raw image if new (DB logic) ---
            # We use the filename from the upload if available
            name = uploaded_file.name if uploaded_file.name else "uploaded_image"
            print(f"LOG: Saving/Checking raw image: {name}")
            raw_image_obj, created = save_image_if_new(pil_img, name=name)
            print(f"LOG: Raw image object ID: {raw_image_obj.id}, New: {created}")

            if created:
                print("LOG: New image uploaded. Invalidating 'all_raw_images_zip' cache.")
                cache.delete("all_raw_images_zip")
            
            # --- Check DB if not in Cache ---
            print("LOG: Checking for existing processed images in DB")
            plots = get_processed_images_from_db(raw_image_obj)

            if plots:
                 # Check if DB has all keys
                 if not all(k in plots for k in expected_keys):
                     print("LOG: Existing DB record missing some plots. Regenerating all...")
                     plots = None # Force regeneration below
                 else:
                     print("LOG: Found existing plots in DB with all keys. Using them.")

            if plots is None:
                # generate new processed images
                print("LOG: Generating new plots...")
                plots = generate_plots_bytes(pil_img)
                print("LOG: Plots generated. Saving/Updating DB...")

                # check if processed object exists
                processed = ProcessedImages.objects(original_image=raw_image_obj).first()
                if processed:
                    print("LOG: Deleting old processed record to ensure clean state.")
                    processed.delete()
                
                processed = ProcessedImages(
                    name="processed_" + (raw_image_obj.name or "image"),
                    original_image=raw_image_obj
                )
                
                # Update all fields
                for key, value in plots.items():
                    # Since it's a fresh object, use put()
                    getattr(processed, key).put(
                        io.BytesIO(value),
                        content_type="image/png"
                    )
                processed.save()
                print("LOG: Processed images saved/updated in DB")
            else:
                pass # Already have valid plots from DB

            # --- Save to Redis ---
            print(f"LOG: Saving plots to Redis with key: {cache_key}")
            cache.set(cache_key, plots, timeout=60 * 5) # Cache for 5 mins

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
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


def list_raw_images(request):
    """
    Reads all images from RawImages (MongoDB GridFS)
    and returns a ZIP containing all images.
    """
    from django.core.cache import cache
    cache_key = "all_raw_images_zip"
    
    print(f"LOG: Checking Redis for key: {cache_key}")
    zip_bytes = cache.get(cache_key)

    if zip_bytes:
        print("LOG: Valid cache entry found for raw images list. Using it.")
    else:
        print("LOG: No cache entry for raw images list. Generating from DB...")
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
        zip_bytes = zip_buffer.getvalue()
        
        print(f"LOG: Saving raw images list to Redis with key: {cache_key}")
        cache.set(cache_key, zip_bytes, timeout=60 * 5)

    response = HttpResponse(zip_bytes, content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="all_raw_images.zip"'
    return response