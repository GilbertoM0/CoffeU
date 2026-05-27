
from django.urls import path
from accounts.views import RegistroUsuarioView, ActivarUsuarioView, LoginView, LogoutView, ForgotPasswordView, ResetPasswordView, UpdateProfileView, FirebaseVerifyView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('registro/', RegistroUsuarioView.as_view(), name='registro'),
    path('activar/', ActivarUsuarioView.as_view(), name='activar'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('forgot/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset/', ResetPasswordView.as_view(), name='reset_password'),
    path('update-profile/', UpdateProfileView.as_view(), name='update_profile'),
    path('firebase-verify/', FirebaseVerifyView.as_view(), name='firebase_verify'),
]