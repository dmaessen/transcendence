from django.shortcuts import render
from django.http import HttpResponse

def landing_page(request):
    # return HttpResponse("hello world")
    return render(request, 'landing_page.html')