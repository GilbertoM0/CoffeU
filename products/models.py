from django.db import models


class Producto(models.Model):

    CATEGORY_CHOICES = [
        ('tablas', 'Tablas'),
        ('bebidasA', 'BebidasA'),
        ('bebidas', 'Bebidas'),
        ('complemento', 'Complemento'),
        ('other', 'Otro'),
    ]

    SIZE_CHOICES = [
        ('U', 'Unico'),
        ('M', 'Mediano'),
        ('L', 'Grande'),
        ('Pzs', 'Piezas'),
        ('Por', 'Porciones'),

    ]

    # Campos base
    name = models.CharField(max_length=255, unique=True, verbose_name='Nombre del producto')
    description = models.TextField(verbose_name='Descripcion del producto')
    stock = models.IntegerField(default=0, verbose_name='Stock disponible')
    imageUrl = models.URLField(max_length=500, blank=True, null=True,
                               verbose_name='URL de la imagen')

    # Categoría del producto
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name='Categoría'
    )

    # Tamaño del producto
    size = models.CharField(
        max_length=10,
        choices=SIZE_CHOICES,
        default='M',
        verbose_name='Tamaño'
    )

    # Precio
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Precio'
    )

    # Calificación
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.0,
        verbose_name='Calificación'
    )

    # Tiempo de entrega (opcional)
    deliveryTime = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Tiempo de Entrega'
    )

    # Distancia (opcional)
    distance = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Distancia'
    )

    # Descuento (opcional)
    discount = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Descuento'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
