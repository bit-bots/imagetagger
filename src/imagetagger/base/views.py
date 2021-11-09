from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse


def index(request):
    return redirect(reverse('images:index'))


def problem_report(request):
    if settings.PROBLEMS_TEXT != '':
        return render(request, 'base/problem.html', {
            'text': settings.PROBLEMS_TEXT
        })
    else:
        return redirect(settings.PROBLEMS_URL)
