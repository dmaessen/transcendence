from data.models import CustomUser, CustomUserManager
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import LoginForm, RegisterForm
from django.http import HttpResponse, JsonResponse

def sign_in(request):
	if request.method == 'GET':
		# user = authenticate(email = 'email', password = 'password')
		if request.user.is_authenticated:
			messages.succes(request, f'already signed in')
			return redirect('game_server')
		form = LoginForm()
		return render(request, 'users/login.html', {'form':form})
	
	if request.method == 'POST':
		form = LoginForm(request.POST)
		# HttpResponse("posted")

		if form.is_valid():
			messages.success(request,f'loaded successfully')
			# email = form.cleaned_data['email']
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(request, username=username, password=password)
			if not username or not password: 
				return HttpResponse("username or password is missing")
			if user is not None:
				login(request, user)
				return HttpResponse("logged in!")
				# return redirect('users/valid.html') #this should probably be home, also SPA?
			else:
				return HttpResponse("user sign in did not work!")
	
	# messages.error(request,f'Invalid username or password')
	# return render(request, 'users/login.html',{'form': form})

def sign_out(request):
	logout(request)
	messages.success(request,f'You have been logged out')
	return HttpResponse("you have been signed out")
	# return redirect('sign_in')

def register(request):
	if request.method == 'GET': 
		form = RegisterForm()
		return render(request, 'users/register.html', {'form': form})
	
	if request.method == 'POST':
		form = RegisterForm(request.POST)

		if form.is_valid():
			user = form.save(commit=False)
			user.name = form.cleaned_data['name']
			user.email = form.cleaned_data['email']
			user.password = form.cleaned_data['password']
			# TODO: store other info, create JWT token and send it insted of using login method
			user.save()
			messages.success(request, 'you have signed up sucesfully.')
			login(request, user)
			return redirect('sign_out')
		else:
			return render(request, 'users/register.html', {'form': form})

def home(request):
	return render(request, 'base.html')
