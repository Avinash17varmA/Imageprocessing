from django.db import models
from mongoengine import Document, StringField, IntField, FileField, ReferenceField

class RawImages(Document):
    name = StringField(max_length=100)
    image = FileField() 
    md5 = StringField(max_length=32, unique=True)
    meta = {
        'collection': 'Raw_Images'
    }

class ProcessedImages(Document):
    name = StringField(max_length=100)
    original_image = ReferenceField(RawImages)  # link to original
    grayscale = FileField()
    scatter = FileField()
    histogram = FileField()
    bar = FileField()
    line = FileField()
    meta = {
        'collection': 'Processed_Images'
    }