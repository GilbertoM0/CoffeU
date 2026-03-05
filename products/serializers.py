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
            'imageUrl',
            'category',
            'size',
            'price',
            'rating',
            'deliveryTime',
            'distance',
            'discount',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer opcionales los campos que se calculan después
        self.fields['deliveryTime'].required = False
        self.fields['distance'].required = False
        self.fields['discount'].required = False