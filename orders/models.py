# orders/models.py

from django.db import models
# Si usas un modelo de usuario personalizado, impórtalo (ej: settings.AUTH_USER_MODEL)
# from django.conf import settings 
from products.models import Producto  # Asumo que tienes un modelo Producto en otra app


class Orders(models.Model):
    """Modelo para representar la Orden o Pedido principal."""

    # 1. Relación con el Usuario (Opcional, pero recomendado)
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuario")

    # 2. Campos recibidos desde el JSON principal:

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Monto Total"
    )

    # Podrías usar un ChoiceField para el estado (ej: 'pendiente', 'enviado', 'entregado')
    estado = models.CharField(
        max_length=50,
        default="pendiente",
        verbose_name="Estado del Pedido"
    )

    # 3. Campos generados por Django (o recibidos):
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )

    # Si quieres la fecha exacta de recepción desde Android:
    # fecha_recepcion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Recepción App")

    def __str__(self):
        return f"Orden #{self.id} - {self.estado}"

    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ['-fecha_creacion']


class OrderItems(models.Model):
    """Modelo para representar los productos individuales dentro de una Orden."""

    # 1. Relación con la Orden (Clave Foránea)
    order = models.ForeignKey(
        Orders,
        related_name='items',  # Este nombre ('items') DEBE coincidir con la clave JSON
        on_delete=models.CASCADE,
        verbose_name="Orden"
    )

    # 2. Relación con el Producto (Clave Foránea)
    # Es mucho mejor usar la clave foránea al modelo Producto en lugar de solo guardar el ID
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,  # Si el producto se borra, el OrderItem se queda
        null=True,
        verbose_name="Producto"
    )

    # 3. Campos recibidos desde el JSON:

    # Nombre del producto (aunque se puede obtener del FK, es bueno guardarlo para historial)
    nombre_producto = models.CharField(
        max_length=255,
        verbose_name="Nombre del Producto"
    )

    cantidad = models.PositiveIntegerField(
        verbose_name="Cantidad"
    )

    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio Unitario"
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Subtotal (Cantidad * Precio)"
    )

    def __str__(self):
        return f"{self.cantidad} x {self.nombre_producto} en Orden #{self.order.id}"

    class Meta:
        verbose_name = "Detalle del Pedido"
        verbose_name_plural = "Detalles del Pedido"
        unique_together = ('order', 'producto')  # Un producto por orden