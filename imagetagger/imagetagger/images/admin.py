from django.contrib import admin

# Register your models here.
from .models import Image, ImageSet

admin.site.register(ImageSet)
admin.site.register(Image)
