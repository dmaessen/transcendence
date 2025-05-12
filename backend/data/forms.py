from django import forms
from django.conf import settings
from .models import CustomUser  # adjust import based on your app structure

class LanguagePreferenceForm(forms.ModelForm):
    preferred_language = forms.ChoiceField(choices=settings.LANGUAGES)

    class Meta:
        model = CustomUser
        fields = ['preferred_language']
