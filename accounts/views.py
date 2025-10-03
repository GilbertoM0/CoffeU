from django.core.serializers import serialize
from django.shortcuts import render
from django.utils.text import normalize_newlines
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Usuario
from accounts.serializers import RegistroUsuarioSerializer,LoginUsuarioSerializer
from accounts.utilities.utils import enviar_otp_mail
from django.utils import timezone


# Create your views here.

class RegistroUsuarioView(APIView):
    def post(self, request):
        serializer = RegistroUsuarioSerializer(data=request.data)
        usuario = None
        if serializer.is_valid():
            usuario = serializer.save()

            # Generar el codigo OTP y enviarlo por correo
            print(f"Codigo OTP: {usuario.otp_codigo}")

            try:
                enviar_otp_mail(usuario)
            except Exception as e:
                return Response({"error": f"No se pudo enviar el OTP por Correo Electrónico: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # Regresamos una respuesta
            return Response({"mensaje": "Usuario registrado. Revisa tu Correo Electrónico"},
                     status=status.HTTP_201_CREATED)
            # return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActivarUsuarioView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        #Verificar que los parametros traigan informacion
        if not email or not otp:
            return Response(
                {"error": "Se requiere email y el código otp de usuario"},
                status=status.HTTP_400_BAD_REQUEST
            )
        #Verificar si existe el usuario
        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Usuario no existe"},
                status=status.HTTP_404_NOT_FOUND
            )
        #Validar el código otp
        if usuario.otp_codigo != otp :
            return Response(
                {"error": "El código OTP de usuario es incorrecto"},
                status=status.HTTP_400_BAD_REQUEST
            )
        #Validar el tiempo del codigo OTP
        tiempo_expiracion = usuario.otp_creado_en + timezone.timedelta(minutes=5)
        if timezone.now() > tiempo_expiracion:
            return Response(
                {"error": "El codigo OTP ah expirado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        #Activar el usuario
        usuario.is_active = True
        usuario.otp_codigo = None
        usuario.save()
        return Response(
            {"mensaje": "Cuenta activada correctamente. Ya puede iniciar sesión"},
            status=status.HTTP_200_OK
        )

class LoginView(APIView):
    permission_classes = []
    def post(self, request):
        serializer = LoginUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response(
                {'error': 'Se requiere un refresh token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"mensaje": "Logged out exitoso"},
                            status=status.HTTP_200_OK
                            )
        except Exception as e:
            return Response({f"error": f"Ocurrio un error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)