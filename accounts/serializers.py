from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.utils import timezone
from rest_framework.validators import UniqueValidator

from accounts.models import Usuario

# Para LOGIN
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class RegistroUsuarioSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=Usuario.objects.all(),
                message="El correo electrónico ya está registrado. Intenta con otro."
            )
        ]
    )

    telefono_celular = serializers.CharField()

    class Meta:
        model = Usuario
        fields = ('nombre_usuario', 'telefono_celular', 'email', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_telefono_celular(self, value):
        # Normalizar a E.164 con prefijo +52 si no lo trae
        if not value.startswith('+'):
            value = '+52' + value
        # Unicidad con el número ya normalizado
        if Usuario.objects.filter(telefono_celular=value).exists():
            raise serializers.ValidationError("El número de teléfono ya está registrado. Intente con otro")
        return value

    def validate(self, validated_data):
        # Verificar las contraseñas
        if validated_data['password'] != validated_data['password2']:
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden'})
        return validated_data

    def create(self, validated_data):
        # Extraer el campo password2
        validated_data.pop('password2')

        # El usuario se crea inactivo; la activación se hace via Firebase Phone OTP
        mi_usuario = Usuario.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nombre_usuario=validated_data['nombre_usuario'],
            telefono_celular=validated_data['telefono_celular'],
            is_active=False,
        )
        return mi_usuario

class LoginUsuarioSerializer(serializers.Serializer):
    # Crear identificador para el email o telefono celular
    identificador = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)

    def validate(self, attrs): #attrs= atributos
        identificador = attrs.get('identificador')
        password = attrs.get('password')
        user = None
        #Intentar autenticar
        user = authenticate(username=identificador, password=password)#Busca usuario que coincida con username
        if user is None:
            # Intentar buscar al usuario por correo electrónico
            try:
                usuario_obj = Usuario.objects.get(email=identificador)
                user = authenticate(username=usuario_obj.telefono_celular, password=password)
                print("Usuario encontrado: ",usuario_obj.telefono_celular)
            except Usuario.DoesNotExist:
                user = None
                print(f"Usuario no encontrado: {identificador}")

        if user is None:
            raise serializers.ValidationError({'error': 'Credeciales invalidas'})
        if not user.is_active:
            raise serializers.ValidationError({'error': 'No esta activada la cuenta'})
        # Generamos los JWT
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        return {
            'refresh_token': str(refresh_token),
            'access_token': str(access_token),
            'user': {
               'id': user.pk,
                'nombre_usuario': getattr(user, 'nombre_usuario', None),
                'email': user.email,
                'telefono_celular': user.telefono_celular,
            },
        }
    def get_user(self, obj):
        return obj.get('user')


class FirebaseVerifyTokenSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=False, allow_blank=True, write_only=True)

    def validate(self, attrs):
        token = attrs.get("id_token")

        if not token:
            data = self.initial_data if isinstance(self.initial_data, dict) else {}
            token = data.get("idToken") or data.get("token") or data.get("firebase_token")

        if not token:
            data = self.initial_data if isinstance(self.initial_data, dict) else {}
            payload = data.get("data")
            if hasattr(payload, "get"):
                token = (
                    payload.get("id_token")
                    or payload.get("idToken")
                    or payload.get("token")
                    or payload.get("firebase_token")
                )

        if not token:
            request = self.context.get("request")
            auth_header = request.headers.get("Authorization", "") if request else ""
            if auth_header.lower().startswith("bearer "):
                token = auth_header.split(" ", 1)[1].strip()

        if not token:
            raise serializers.ValidationError(
                {"detail": "Se requiere id_token (o idToken) en el body, o Authorization: Bearer <token>."}
            )

        attrs["id_token"] = token
        return attrs

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    telefono_celular = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        email = (attrs.get('email') or '').strip() or None
        telefono = (attrs.get('telefono_celular') or '').strip() or None

        if not email and not telefono:
            raise serializers.ValidationError("Debes proporcionar los campos de entrada, email o telefono")

        try:
            if email:
                usuario = Usuario.objects.get(email=email)
            else:
                usuario = Usuario.objects.get(telefono_celular=telefono)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontraduquis")

        #Generar OTP y guardarlo
        otp = Usuario.generar_otp()
        usuario.otp_codigo = otp
        usuario.otp_creado_en = timezone.now()
        usuario.save()

        # OTP generado para flujo de recuperacion por mensajes (Firebase/app)
        print(f" OTP de recuperacion: {otp}")
        attrs["usuario"] = usuario
        return attrs

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    telefono_celular = serializers.CharField(required=False)
    otp = serializers.CharField()
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        telefono = attrs.get('telefono_celular')
        otp = attrs.get('otp')

        if not email and not telefono:
            raise serializers.ValidationError("Debes proporcionar los campos de entrada, email o telefono")
        try:
            if email:
                usuario = Usuario.objects.get(email=email)
            else:
                usuario = Usuario.objects.get(telefono_celular=telefono)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")

        #Validar OTP
        if usuario.otp_codigo != otp:
            raise serializers.ValidationError(f"OTP de recuperacion no coinciden, invalido")

        tiempo_expiracion = usuario.otp_creado_en + timezone.timedelta(minutes=5)
        if timezone.now() > tiempo_expiracion:
            raise serializers.ValidationError("El código OTP ha expirado")

        #Validar contraseñas
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError("Las contraseñas no coinciden")

        attrs["usuario"] = usuario
        return attrs

    def save(self, **kwargs):
        usuario = self.validated_data['usuario']
        usuario.password = make_password(self.validated_data['new_password'])
        usuario.otp = None #Invalidar OTP
        usuario.save()
        return usuario



class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = (
            'nombre_usuario',
            'email',
            'telefono_celular',
            'bio',
            'genero',
            'fecha_nacimiento',
            'intereses',
            'avatar',
        )

class UpdateUserProfileSerializer(serializers.ModelSerializer):
    # Definimos los campos explícitamente para validación, pero sin UniqueValidator estático
    # para poder manejar la exclusión del propio usuario en la validación.
    email = serializers.EmailField()
    telefono_celular = serializers.CharField()

    class Meta:
        model = Usuario
        fields = ('nombre_usuario', 'email', 'telefono_celular', 'fecha_nacimiento')

    def validate_email(self, value):
        user = self.context['request'].user
        # Verificamos si existe otro usuario con este email, excluyendo al actual
        if Usuario.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("El correo electrónico ya está registrado. Intenta con otro.")
        return value

    def validate_telefono_celular(self, value):
        user = self.context['request'].user
        # Verificamos si existe otro usuario con este teléfono, excluyendo al actual
        if Usuario.objects.exclude(pk=user.pk).filter(telefono_celular=value).exists():
            raise serializers.ValidationError("El número de teléfono ya está registrado. Intente con otro.")
        return value

