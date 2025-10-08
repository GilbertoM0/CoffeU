
from django.urls import path

from accounts.serializers import LoginUsuarioSerializer
from accounts.views import RegistroUsuarioView, ActivarUsuarioView, LoginView, LogoutView, ForgotPasswordView,ResetPasswordView
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path('registro/', RegistroUsuarioView.as_view(), name='registro'),
    path('activar/', ActivarUsuarioView.as_view(), name='activar'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('forgot/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset/', ResetPasswordView.as_view(), name='reset_password'),


]