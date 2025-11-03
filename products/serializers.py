from rest_framework import serializers

from products.models import Producto


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        #Define el modelo
        model = Producto

        #Lista los campos que deben incluirse en la API
        fields = [
            'id',
            'name',
            'description',
            'stock',
            'imageUrl',  # Renombrado

            # Nuevos campos (ya coinciden con models.py)
            'price',
            'rating',
            'reviewCount',
            'deliveryTime',
            'distance',
            'discount',
        ]