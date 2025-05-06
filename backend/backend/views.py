from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
import os
from django.conf import settings
from django.shortcuts import render
from django.utils import translation

# def index(request):
#     return render(request, 'index.html')

def index(request):
    current_language = translation.get_language()
    
    context = {
        'LANGUAGE_CODE': current_language,
        # Other context variables...
    }
    
    return render(request, 'index.html', context)
