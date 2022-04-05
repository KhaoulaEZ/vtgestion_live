from django.urls import path
from . import views
from django.contrib.auth import views as auth_view
from django.views.generic import TemplateView

from .views import forgot_password, activateAccount, reset_password, change_user_account_activation

urlpatterns = [
    #path('', views.login, name='login'),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('login/', auth_view.LoginView.as_view(template_name='users/login.html'), name="login"),
    path('logout/', auth_view.LogoutView.as_view(template_name='users/logout.html'), name="logout"),
    path('activate/<str:uid>/<str:token>', views.activateAccount),
    path('forgot_password/', views.forgot_password),
    path('password/reset/confirm/<str:uid>/<str:token>',views. reset_password),
    path('user/change/activation/', views.change_user_account_activation),
]
