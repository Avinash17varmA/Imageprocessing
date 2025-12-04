from django.urls import path
from . import views

urlpatterns = [
    path('upload-image/', views.upload_image, name='upload-image'),
    path('test/', views.test, name='test'),
    path('raw-images/', views.list_raw_images, name='raw_images'),

]
