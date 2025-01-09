from django import forms

class LoginForm(forms.Form):
	usernam = forms.charfield(max_lenght=65)
	password = forms.Charfield(max_langht=65, widget=forms.PasswordInput)

