# orders/urls.py (COMPLETO PARA CRUD)

from django.urls import path
from .views import OrderListCreateView, OrderDetailView

urlpatterns = [
    # 1. LISTADO (GET) y CREACIÓN (POST)
    # Ejemplo de URL: /api/orders/
    path('', OrderListCreateView.as_view(), name='order-list-create'),

    # 2. DETALLE (GET), ACTUALIZACIÓN (PUT/PATCH) y BORRADO (DELETE)
    # Ejemplo de URL: /api/orders/1/
    # El <int:pk> captura el ID de la orden.
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
]