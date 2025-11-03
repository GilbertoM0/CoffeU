from django.db import models

class Producto(models.Model):
    # Campos existentes, renombrados en inglés/camelCase para la sincronización
    name = models.CharField(max_length=255, unique=True, verbose_name='Nombre del producto')
    description = models.TextField(verbose_name='Descripcion del producto')
    stock = models.IntegerField(default=0, verbose_name='Stock disponible')
    imageUrl = models.URLField(max_length=500, blank=True, null=True,
                               verbose_name='URL de la imagen')  # Renombrado a imageUrl

    # CAMPOS AÑADIDOS
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Precio'
    )

    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.0,
        verbose_name='Calificación'
    )

    # Renombrado para que coincida directamente con 'reviewCount' en Kotlin
    reviewCount = models.IntegerField(
        default=0,
        verbose_name='Número de Reseñas'
    )

    # Renombrado para que coincida directamente con 'deliveryTime' en Kotlin
    deliveryTime = models.CharField(
        max_length=50,
        default='15-30 min',
        verbose_name='Tiempo de Entrega'
    )

    # Renombrado para que coincida directamente con 'distance' en Kotlin
    distance = models.CharField(
        max_length=50,
        default='1.0 km',
        verbose_name='Distancia'
    )

    # Renombrado para que coincida directamente con 'discount' en Kotlin
    discount = models.CharField(
        max_length=50,
        default='0% Off',
        verbose_name='Descuento'
    )

    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
