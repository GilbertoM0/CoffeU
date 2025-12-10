# orders/views.py (COMPLETO PARA CRUD)

from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import OrderSerializer
from .models import Orders

# =================================================================
# 1. Vista para LISTAR (GET) y CREAR (POST)
# URL: /api/orders/
# =================================================================
class OrderListCreateView(generics.ListCreateAPIView):
    """
    Maneja GET (lista todas las órdenes) y POST (crea una nueva orden).
    """
    serializer_class = OrderSerializer
    queryset = Orders.objects.all()
    # Usar IsAuthenticated si quieres que solo usuarios logueados accedan
    permission_classes = [AllowAny]


# =================================================================
# 2. Vista para DETALLE (GET), ACTUALIZAR (PUT/PATCH) y BORRAR (DELETE)
# URL: /api/orders/<id>/
# =================================================================
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Maneja GET, PUT, PATCH y DELETE para una orden específica usando su ID (pk).
    """
    serializer_class = OrderSerializer
    queryset = Orders.objects.all()
    permission_classes = [AllowAny]