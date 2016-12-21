from django.contrib import admin

# Register your models here.
from .models import ImageSet, Image, Annotation, AnnotationType, Export 

admin.site.register(ImageSet)
admin.site.register(Image)
admin.site.register(Annotation)
admin.site.register(AnnotationType)
admin.site.register(Export)
