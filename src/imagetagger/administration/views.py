from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction

from .forms import AnnotationTypeCreationForm, AnnotationTypeEditForm
from imagetagger.annotations.models import Annotation, AnnotationType


@staff_member_required
def annotation_types(request):
    return render(request, 'administration/annotation_type.html', {
        'annotation_types': AnnotationType.objects.all().order_by('name'),
        'create_form': AnnotationTypeCreationForm,
    })


@staff_member_required
def annotation_type(request, annotation_type_id):
    selected_annotation_type = get_object_or_404(AnnotationType, id=annotation_type_id)
    return render(request, 'administration/annotation_type.html', {
        'annotation_types': AnnotationType.objects.all().order_by('name'),
        'annotation_type': selected_annotation_type,
        'vector_type_name': AnnotationType.get_vector_type_name(selected_annotation_type.vector_type),
        'create_form': AnnotationTypeCreationForm(),
        'edit_form': AnnotationTypeEditForm(instance=selected_annotation_type)
    })


@staff_member_required
def create_annotation_type(request):
    if request.method == 'POST':
        form = AnnotationTypeCreationForm(request.POST)

        if form.is_valid():
            if AnnotationType.objects.filter(name=form.cleaned_data.get('name')).exists():
                form.add_error(
                    'name',
                    _('The name is already in use by an annotation type.'))
            else:
                with transaction.atomic():

                    type = form.save()

                messages.success(request, _('The annotation type was created successfully.'))
                return redirect(reverse('administration:annotation_type', args=(type.id,)))
    else:
        return redirect(reverse('administration:annotation_types'))


@staff_member_required
def edit_annotation_type(request, annotation_type_id):
    selected_annotation_type = get_object_or_404(AnnotationType, id=annotation_type_id)
    if request.method == 'POST':
        if not request.POST['name'] == selected_annotation_type.name and AnnotationType.objects.filter(name=request.POST['name']).exists():
            messages.error(request, _('The name is already in use by an annotation type.'))
        else:
            selected_annotation_type.name = request.POST['name']
            selected_annotation_type.active = 'active' in request.POST.keys()
            selected_annotation_type.enable_concealed = 'enable_concealed' in request.POST.keys()
            selected_annotation_type.enable_blurred = 'enable_blurred' in request.POST.keys()
            selected_annotation_type.save()

            messages.success(request, _('The annotation type was edited successfully.'))
    return redirect(reverse('administration:annotation_type', args=(annotation_type_id, )))


@staff_member_required
def migrate_bounding_box_to_0_polygon(request, annotation_type_id):
    selected_annotation_type = get_object_or_404(AnnotationType, id=annotation_type_id)

    if selected_annotation_type.vector_type is AnnotationType.VECTOR_TYPE.BOUNDING_BOX:
        annotations = Annotation.objects.filter(annotation_type=selected_annotation_type)
        for annotation in annotations:
            annotation.verifications.all().delete()
            if annotation.vector:
                annotation.vector = {
                    'x1': annotation.vector['x1'],
                    'y1': annotation.vector['y1'],
                    'x2': annotation.vector['x2'],
                    'y2': annotation.vector['y1'],
                    'x3': annotation.vector['x2'],
                    'y3': annotation.vector['y2'],
                    'x4': annotation.vector['x1'],
                    'y4': annotation.vector['y2'],
                }
            annotation.save()
        selected_annotation_type.vector_type = AnnotationType.VECTOR_TYPE.POLYGON
        selected_annotation_type.node_count = 0
        selected_annotation_type.save()
    return redirect(reverse('administration:annotation_type', args=(annotation_type_id, )))


@staff_member_required
def migrate_bounding_box_to_4_polygon(request, annotation_type_id):
    selected_annotation_type = get_object_or_404(AnnotationType, id=annotation_type_id)

    if selected_annotation_type.vector_type is AnnotationType.VECTOR_TYPE.BOUNDING_BOX:
        annotations = Annotation.objects.filter(annotation_type=selected_annotation_type)
        for annotation in annotations:
            annotation.verifications.all().delete()
            if annotation.vector:
                annotation.vector = {
                    'x1': annotation.vector['x1'],
                    'y1': annotation.vector['y1'],
                    'x2': annotation.vector['x2'],
                    'y2': annotation.vector['y1'],
                    'x3': annotation.vector['x2'],
                    'y3': annotation.vector['y2'],
                    'x4': annotation.vector['x1'],
                    'y4': annotation.vector['y2'],
                }
            annotation.save()
        selected_annotation_type.vector_type = AnnotationType.VECTOR_TYPE.POLYGON
        selected_annotation_type.node_count = 4
        selected_annotation_type.save()
    return redirect(reverse('administration:annotation_type', args=(annotation_type_id, )))
