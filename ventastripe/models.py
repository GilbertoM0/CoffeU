# ventastripe/models.py

from django.db import models
from django.contrib.auth import get_user_model
# Importa el modelo Producto desde la app 'products'
from products.models import Producto

User = get_user_model()


# --- MODELO PRINCIPAL: ORDER ---
class Order(models.Model):
    # 1. Relación con el usuario (apunta a accounts.Usuario)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name='Usuario')

    # 2. Información clave del pago/transacción de Stripe
    stripe_session_id = models.CharField(max_length=255, unique=True, null=True, blank=True,
                                         verbose_name='ID de Sesión de Stripe')

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                       verbose_name='Monto Total')

    # 3. Estado de la Orden
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),  # Creada, esperando el pago
        ('paid', 'Pagada'),  # Confirmada por Webhook de Stripe
        ('shipped', 'Enviada'),
        ('delivered', 'Entregada'),
        ('cancelled', 'Cancelada'),
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending',
                              verbose_name='Estado de la Orden')

    # 4. Tiempos
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')

    class Meta:
        verbose_name = 'Orden de Compra'
        verbose_name_plural = 'Órdenes de Compra'
        ordering = ['-created_at']

    def calculate_total(self):
        # Recalcula el total de todos los items en la orden
        total = sum(item.get_subtotal() for item in self.items.all())
        self.total_amount = total
        self.save()
        return total


# --- MODELO SECUNDARIO: ÍTEM DE LA ORDEN ---
class OrderItem(models.Model):
    # 1. Relación con la orden
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE,
                              verbose_name='Orden')

    # 2. Relación con el producto. Usamos ForeignKey a products.Producto.
    product = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True,
                                verbose_name='Producto')

    # 3. Datos del producto al momento de la compra
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2,
                                            verbose_name='Precio al momento de la compra')

    quantity = models.PositiveIntegerField(default=1, verbose_name='Cantidad')

    class Meta:
        verbose_name = 'Ítem de la Orden'
        verbose_name_plural = 'Ítems de la Orden'

    def get_subtotal(self):
        return self.price_at_purchase * self.quantity