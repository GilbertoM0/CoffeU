
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

    telefono_celular = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Usuario.objects.all(),
                message="El número de teléfono ya está registrado. Intente con otro"
            )
        ]
    )

    class Meta:
        model = Usuario
        fields = ('nombre_usuario', 'telefono_celular', 'email', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, validated_data):
        # Verificar las conttraseñas
        if validated_data['password'] != validated_data['password2']:
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden'})
        return validated_data

    def create(self, validated_data):
        # Extraer el campo password2
        validated_data.pop('password2')

        # Generar el OTP
        otp = Usuario.generar_otp()

        mi_usuario = Usuario.objects.create_user( # Usuario.objects.create_user(  # Para que pase por las validaciones de DRF
            email=validated_data['email'],
            password=validated_data['password'],
            nombre_usuario=validated_data['nombre_usuario'],
            telefono_celular=validated_data['telefono_celular'],
            is_active=False,
            otp_codigo = otp,
            otp_creado_en = timezone.now()
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