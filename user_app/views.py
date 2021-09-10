#from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404 #追加
from .forms import SignUpForm
from django.contrib.auth import authenticate, login
from production .models import ProdUser
from django.contrib.auth.models import User

# Create your views here.
def signup(request):
  signup_form = SignUpForm(request.POST or None)
  if request.method == "POST" and signup_form.is_valid():
      user = signup_form.save()
      input_username = signup_form.cleaned_data['username']
      input_email = signup_form.cleaned_data['email']
      input_password = signup_form.cleaned_data['password1']
      user = authenticate(username=input_username, email=input_email, password=input_password)
      login(request, user)
      return redirect('production:root')
  context = {
      "signup_form": signup_form,
  }
  return render(request, 'user_app/signup.html', context)
