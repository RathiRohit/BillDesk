from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
	full_name = forms.CharField(max_length=100)
	mob_number = forms.CharField(max_length=15)
	email_id = forms.EmailField(max_length=254)
	
	class Meta:
		model = User
		fields = ('full_name', 'username', 'mob_number', 'email_id', 'password1', 'password2')