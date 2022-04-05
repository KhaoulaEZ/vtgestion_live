from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .Forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_view
from . import views
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

def home(request):
    return render(request, 'users/home.html')

def login(request):
    return render(request,'users/login.html')
def activateAccount(request,uid,token):
    return render(request, 'activate.html', {'uid':uid,'token':token})

def forgot_password(request):
    return render(request, 'forget_pwr.html',{})

def reset_password(request,uid,token):
    return render(request, 'rest_pwr.html', {'uid':uid,'token':token})
@csrf_exempt
def change_user_account_activation(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(email=request.POST.get('email'))
            is_activated = True if request.POST.get('active') == 'true' else False
            if user:
                user.activated = is_activated
                user.save()
                key = 'Activated' if is_activated else 'Deactivated'
                json_response = {"success": True, "Message": 'User ' + key + ' Successfully'}
            else:
                json_response = {"error": "User Not Found", "success": False}
        except Exception as ex:
            json_response = {"error": str(ex), "success": False}
    else:
        json_response = {"error": 'Not Allowed Method', "success": False}
    return JsonResponse(json_response)

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hi {username}, your account was created successfully')
            return redirect('home')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


@login_required()
def profile(request):
    return render(request, 'users/profile.html')

########list###
