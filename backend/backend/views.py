from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
import os
from django.conf import settings

def index(request):
    return render(request, 'index.html')
