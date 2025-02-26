from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .productsDetails import products
from .models import Product
from base.serializer import ProductSerializer
from django.shortcuts import get_object_or_404


# Create your views here.

@api_view(['GET'])
def getRoutes(_):
    routes = [

    ]
    return Response('Hello')

@api_view(['GET'])
def getProducts(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getProduct(request, pk):
    product = Product.objects.get(id=int(pk))
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)