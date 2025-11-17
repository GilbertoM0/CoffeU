from rest_framework import serializers
from .models import VentaSemanal

class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VentaSemanal
        fields = '__all__'
