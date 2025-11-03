from django.shortcuts import render
from rest_framework import viewsets

from products.models import Producto
from products.serializers import ProductSerializer

# ModelViewSet proporciona las acciones CRUD (list, retrieve, create, update, destroy)
class ProductViewSet(viewsets.ModelViewSet):
    #La consulta que se usara para obtener los objetos (todos los productos)
    queryset = Producto.objects.all().order_by('name')
    #El serializer que se usara para convertir los objetos
    serializer_class = ProductSerializer
