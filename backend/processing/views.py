from django.http import JsonResponse

# Basic API view
def hello_world(request):
    return JsonResponse({"message": "Hello World from Django backend!"})
