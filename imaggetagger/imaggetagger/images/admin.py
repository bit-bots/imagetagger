from django.contrib import admin

# Register your models here.
from .models import ImageSet, Image, Annotation, AnnotationType, Export, Verification

admin.site.register(ImageSet)
admin.site.register(Image)
admin.site.register(Annotation)
admin.site.register(AnnotationType)
admin.site.register(Export)
admin.site.register(Verification)
