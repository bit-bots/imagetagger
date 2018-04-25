from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction

from .forms import AnnotationTypeCreationForm, AnnotationTypeEditForm
from imagetagger.annotations.models import AnnotationType


@staff_member_required
def annotation_types(request):
    return render(request, 'administration/annotation_type.html', {
        'annotation_types': AnnotationType.objects.all(),
        'create_form': AnnotationTypeCreationForm,
    })


@staff_member_required
def annotation_type(request, annotation_type_id):
    selected_annotation_type = get_object_or_404(AnnotationType, id=annotation_type_id)
    return render(request, 'administration/annotation_type.html', {
        'annotation_types': AnnotationType.objects.all().order_by('name'),
        'annotation_type': selected_annotation_type,
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
        form = AnnotationTypeEditForm(request.POST)

        if form.is_valid():
            if form.instance.name is not selected_annotation_type.name and AnnotationType.objects.filter(name=form.cleaned_data.get('name')).exists():
                form.add_error(
                    'name',
                    _('The name is already in use by an annotation type.'))
            else:
                selected_annotation_type.name = form.instance.name
                selected_annotation_type.node_count = form.instance.node_count
                selected_annotation_type.active = form.instance.active
                selected_annotation_type.save()

                messages.success(request, _('The annotation type was edited successfully.'))
    return redirect(reverse('administration:annotation_type', args=(annotation_type_id, )))