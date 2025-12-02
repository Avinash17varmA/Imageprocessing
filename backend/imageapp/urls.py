from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('backend/', include('processing.urls')),  # ✅ include your app URLs
]
