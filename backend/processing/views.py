from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import uuid
from django.http import JsonResponse, HttpResponse

# Basic API view
@csrf_exempt
def upload_image(request):
    if request.method == "POST":
        image_bytes = request.body  # raw binary data

        # Save image
        filename = f"{uuid.uuid4()}.jpg"
        with open(filename, "wb") as f:
            f.write(image_bytes)

        # Return SAME image back
        return HttpResponse(image_bytes, content_type="image/jpeg")

    return JsonResponse({"error": "Use POST"})
