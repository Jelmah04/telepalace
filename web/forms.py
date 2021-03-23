from django import forms
from django.core.exceptions import ValidationError ### We might need this for Validation else we do it in views.py.
from django.contrib.auth.forms import UserCreationForm, UserChangeForm ### We call the default django here to build custom for it.
from django.contrib.auth import get_user_model

User = get_user_model() ### We need to override the default Django User Model here


class SignUpForm(UserCreationForm):
  first_name = forms.CharField(max_length=30)
  last_name = forms.CharField(max_length=30)
  username = forms.CharField(max_length=30)
  email = forms.EmailField(max_length=200)
  mobile = forms.CharField(max_length=200)

  class Meta:
      model = User
      fields = ('username', 'email', 'first_name', 'last_name', 'mobile', 'password1', 'password2', )
