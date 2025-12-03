# ventastripe/serializers.py

from rest_framework import serializers
from products.models import Producto


class OrderItemSerializer(serializers.Serializer):
    """
    Valida un solo ítem de un carrito de compras.
    """
    id = serializers.IntegerField(help_text="ID del producto a comprar.")
    quantity = serializers.IntegerField(min_value=1, help_text="Cantidad del producto.")

    def validate_id(self, value):
        # 1. Verificar si el producto existe
        try:
            producto = Producto.objects.get(id=value)
        except Producto.DoesNotExist:
            raise serializers.ValidationError(f"El producto con ID {value} no existe.")

        # Guardar la instancia para usarla en validate()
        self.producto_instance = producto
        return value

    def validate(self, data):
        producto = self.producto_instance
        quantity = data['quantity']

        # 2. Verificar Stock
        if producto.stock < quantity:
            raise serializers.ValidationError(
                {'quantity': f"Stock insuficiente para {producto.name}. Quedan {producto.stock} en inventario."}
            )

        # Adjuntar datos necesarios a la respuesta validada
        data['price'] = producto.price
        data['name'] = producto.name
        data['product_instance'] = producto

        return data


class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer principal que recibe toda la lista del carrito del Frontend.
    """
    cart_items = OrderItemSerializer(many=True, help_text="Lista de productos y cantidades a comprar.")

    def validate_cart_items(self, value):
        if not value:
            raise serializers.ValidationError("La orden no puede estar vacía.")
        return value