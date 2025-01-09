from django.shortcuts import render
from .forms import LoginForm

from django.http import HttpResponse, JsonResponse

def sign_in(request):
	if request.method == 'GET':
		form = LoginForm()
		return render(request, 'users/login.html', {'form':form})
