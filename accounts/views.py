from django.utils import timezone
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Usuario
from accounts.serializers import (
    ForgotPasswordSerializer,
    LoginUsuarioSerializer,
    RegistroUsuarioSerializer,
    ResetPasswordSerializer,
    UpdateUserProfileSerializer,
)
from accounts.utilities.utils import enviar_otp_mail


class RegistroUsuarioView(APIView):
    def post(self, request):
        serializer = RegistroUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()

            print(f"Codigo OTP: {usuario.otp_codigo}")

            try:
                enviar_otp_mail(usuario)
            except Exception as e:
                return Response(
                    {"error": f"No se pudo enviar el OTP por Correo Electronico: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {"mensaje": "Usuario registrado. Revisa tu Correo Electronico"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivarUsuarioView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response(
                {"error": "Se requiere email y el codigo otp de usuario"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Usuario no existe"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if usuario.otp_codigo != otp:
            return Response(
                {"error": "El codigo OTP de usuario es incorrecto"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tiempo_expiracion = usuario.otp_creado_en + timezone.timedelta(minutes=5)
        if timezone.now() > tiempo_expiracion:
            return Response(
                {"error": "El codigo OTP ha expirado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario.is_active = True
        usuario.otp_codigo = None
        usuario.save()
        return Response(
            {"mensaje": "Cuenta activada correctamente. Ya puede iniciar sesion"},
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "Se requiere un refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"mensaje": "Logged out exitoso"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Ocurrio un error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"mensaje": "Se envio OTP para restablecer tu contrasena"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"mensaje": "Contrasena restablecida correctamente"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileView(RetrieveUpdateAPIView):
    serializer_class = UpdateUserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
