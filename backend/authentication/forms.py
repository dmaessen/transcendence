from django import forms
from data.models import CustomUser, CustomUserManager
# from django.contrib.auth.models import User, UserManager

from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class LoginForm(forms.Form):
	username = forms.CharField(max_length=65)
	password = forms.CharField(max_length=65, widget=forms.PasswordInput)

class RegisterForm(forms.Form):
	name = forms.CharField(max_length=150)
	email = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput)
	repeat_password = forms.CharField(widget=forms.PasswordInput)

	def clean(self):
		cleaned_data = super().clean()
		password = cleaned_data.get('password')
		repeat_password = cleaned_data.get('repeat_password')

	#validation to ensure passwords match
		if password and repeat_password and password != repeat_password:
			raise forms.ValidationError("Passwords do not match.")
        
		return cleaned_data

	def save(self, commit=True):
		cleaned_data = self.cleaned_data
		name = cleaned_data['name']
		email = cleaned_data['email']
		password = cleaned_data['password']
        
		user = CustomUser(name = name, email = email)
		user.set_password(password)

		if commit:
			user.save()
		
		return user
