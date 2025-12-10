# orders/serializers.py

from rest_framework import serializers
from .models import Orders, OrderItems
from products.models import Producto  # Asegúrate que esta importación sea correcta


# =================================================================
# 1. SERIALIZER ANIDADO (Para los "items" del pedido)
# =================================================================

class OrderItemSerializer(serializers.ModelSerializer):
    # En el JSON de Android, envías "producto_id" (un entero).
    # Este campo nos permite recibir el ID y asignarlo al campo 'producto' (ForeignKey)
    producto_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItems
        fields = [
            'producto_id',  # Para recibir el ID del producto de Android
            'nombre_producto',  # Del JSON: "nombre_producto": "Cold coffee"
            'cantidad',  # Del JSON: "cantidad": 2
            'precio_unitario',  # Del JSON: "precio_unitario": 45
            'subtotal'  # Del JSON: "subtotal": 90
        ]


# =================================================================
# 2. SERIALIZER PRINCIPAL (Para la Orden completa)
# =================================================================

class OrderSerializer(serializers.ModelSerializer):
    # 'items' es el campo de relación definido en models.py (related_name='items')
    # many=True indica que es una lista de OrderItems.
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Orders
        fields = [
            'id',
            'items',  # La lista de productos anidados
            'total',  # Del JSON: "total": 90
            'estado',  # Del JSON: "estado": "pendiente"
            'fecha_creacion',  # (Lectura) Generado por Django
            # 'fecha_recepcion'     # (Si lo usas)
        ]
        # Estos campos son solo de lectura, ya que Django los genera o no los necesita de la entrada directa
        read_only_fields = ['fecha_creacion', 'id']

        # =================================================================

    # 3. MÉTODO CREATE OVERRIDE (Lógica para guardar la Orden y sus Items)
    # =================================================================
    def create(self, validated_data):
        # 1. Extraer los items anidados de los datos validados
        items_data = validated_data.pop('items')

        # 2. Crear la Orden (Orders) principal
        order = Orders.objects.create(**validated_data)

        # 3. Iterar y crear cada OrderItem
        for item_data in items_data:
            # Recuperar el ID del producto enviado desde Android
            producto_id = item_data.pop('producto_id')

            # Buscar el objeto Producto (necesario para la ForeignKey)
            try:
                producto = Producto.objects.get(id=producto_id)
            except Producto.DoesNotExist:
                raise serializers.ValidationError(f"El Producto con ID {producto_id} no existe.")

            # Crear el OrderItem y vincularlo a la Orden
            OrderItems.objects.create(
                order=order,
                producto=producto,  # Asignar la ForeignKey
                **item_data
            )

        return order