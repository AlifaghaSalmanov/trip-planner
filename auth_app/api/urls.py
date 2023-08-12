from django.contrib import admin
from django.urls import path, include
from auth_app.api import views
from knox.views import LogoutView
from rest_framework.authtoken.views import obtain_auth_token
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm, reset_password_validate_token
from rest_framework import routers

urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name='auth'),
    path('logout/', LogoutView.as_view(), name='auth'),
    path('user-edit/', views.UserEditAPIView.as_view(), name='auth'),
    path('registration/', views.UserRegisterAPIView.as_view(), name='auth'),
    path('me/', views.MeAPIView.as_view(), name='auth'),

    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),

    path('password-reset/validate-token/', reset_password_validate_token, name="reset-password-validate"),
    path('password-reset/confirm/', reset_password_confirm, name="reset-password-confirm"),
    path('password-reset/', reset_password_request_token, name="reset-password-request"),

    path('activate/', views.UserActivationView.as_view(), name='activate'),
]