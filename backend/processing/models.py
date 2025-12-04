from django.db import models
from mongoengine import Document, StringField, IntField, FileField

class Book(Document):
    title = StringField(required=True, max_length=100)
    author = StringField(max_length=50)

    meta = {
        'collection': 'my_books'
    }

class RawImages(Document):
    name = StringField(max_length=100)
    image = FileField() 
    meta = {
        'collection': 'Raw_Images'
    }