from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import Usuario
from accounts.serializers import RegistroUsuarioSerializer, LoginUsuarioSerializer, ForgotPasswordSerializer,ResetPasswordSerializer, UpdateProfileSerializer, FirebaseVerifyTokenSerializer
from accounts.utilities.utils import validar_token_firebase
from django.utils import timezone
from firebase_admin import auth as firebase_auth
import logging

logger = logging.getLogger(__name__)


# Create your views here.

class RegistroUsuarioView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegistroUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"mensaje": "Usuario registrado. Verifica tu número de teléfono con el código enviado por Firebase."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FirebaseVerifyView(APIView):
    """Recibe el ID token de Firebase Phone Auth, lo verifica y activa la cuenta."""
    permission_classes = [AllowAny]
    authentication_classes = []

    @staticmethod
    def _buscar_usuario_por_telefono(phone_number):
        candidates = [phone_number]
        if phone_number and phone_number.startswith('+52'):
            candidates.append(phone_number[3:])

        for telefono in candidates:
            try:
                return Usuario.objects.get(telefono_celular=telefono)
            except Usuario.DoesNotExist:
                continue
        return None

    @staticmethod
    def _buscar_usuario_por_google(email, uid):
        if email:
            try:
                return Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                pass

        if uid:
            try:
                return Usuario.objects.get(nombre_usuario=uid)
            except Usuario.DoesNotExist:
                pass

        return None

    def post(self, request):
        serializer = FirebaseVerifyTokenSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(
                {"detail": serializer.errors.get("detail", "Request invalido")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        id_token = serializer.validated_data["id_token"]

        try:
            claims = validar_token_firebase(id_token)
        except firebase_auth.ExpiredIdTokenError:
            return Response(
                {"detail": "Token de Firebase expirado. Solicita un token nuevo desde la app."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except firebase_auth.RevokedIdTokenError:
            return Response(
                {"detail": "Token de Firebase revocado."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except firebase_auth.InvalidIdTokenError as e:
            return Response(
                {"detail": f"Token de Firebase invalido: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error("Error validando Firebase token: %s: %s", type(e).__name__, e)
            return Response(
                {"detail": f"No se pudo validar el token Firebase ({type(e).__name__})."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        uid = claims.get("uid")
        email = claims.get("email")
        phone_number = claims.get("phone_number")
        provider = claims.get("sign_in_provider")

        usuario = None
        if provider == "phone":
            if not phone_number:
                return Response(
                    {"detail": "Token de Phone Auth sin phone_number. Verifica el flujo de Firebase Phone."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            usuario = self._buscar_usuario_por_telefono(phone_number)
        elif provider == "google.com":
            usuario = self._buscar_usuario_por_google(email, uid)
        else:
            return Response(
                {
                    "detail": f"Proveedor de autenticacion no soportado: {provider}",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if usuario is None:
            return Response(
                {
                    "detail": "No se encontro un usuario vinculado con este token. Usa telefono (phone) o email/uid (google)."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Activar cuenta
        usuario.is_active = True
        usuario.otp_codigo = None
        usuario.save()

        # Emitir JWT
        refresh = RefreshToken.for_user(usuario)
        return Response({
            "mensaje": "Autenticacion Firebase exitosa",
            "provider": provider,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": {
                "id": usuario.pk,
                "nombre_usuario": usuario.nombre_usuario,
                "email": usuario.email,
                "telefono_celular": usuario.telefono_celular,
            }
        }, status=status.HTTP_200_OK)

class ActivarUsuarioView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

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
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

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

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"mensaje": "OTP de recuperacion generado. Completa la validacion por mensajes en la app."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"mensaje": "Contraseña restablecida correctamente"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UpdateProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UpdateProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "mensaje": "Perfil actualizado correctamente",
                    "usuario": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

