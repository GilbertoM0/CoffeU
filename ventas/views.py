from rest_framework import viewsets
from .models import VentaSemanal
from .serializers import VentaSerializer

class VentaViewSet(viewsets.ModelViewSet):
    queryset = VentaSemanal.objects.all()
    serializer_class = VentaSerializer
