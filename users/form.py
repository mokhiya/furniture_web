from django import forms
from django.contrib.auth.models import User


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')


class LoginForm(forms.Form):
    username = forms.CharField(max_length=128)
    password = forms.CharField(max_length=128)