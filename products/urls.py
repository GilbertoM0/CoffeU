
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from accounts.serializers import LoginUsuarioSerializer
from accounts.views import RegistroUsuarioView, ActivarUsuarioView, LoginView, LogoutView, ForgotPasswordView,ResetPasswordView
from rest_framework_simplejwt.views import TokenRefreshView

from products.views import ProductViewSet

# DefaultRouter registra automáticamente las URLs para el ViewSet
router = DefaultRouter()
router.register(r'', ProductViewSet)# 'products' será el prefijo de la URL

urlpatterns = [
    path('', include(router.urls))
]