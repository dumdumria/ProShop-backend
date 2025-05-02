from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from base.models import Product, Order, OrderItem, ShippingAddress
from base.serializer import ProductSerializer, OrderSerializer

from rest_framework import status
from datetime import datetime


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):

    user = request.user
    data = request.data

    orderItems = data.get('orderItems', [])
    if not orderItems or len(orderItems) == 0:
        return Response({'detail': 'No Order Items'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        tax_price = float(data['taxPrice'])
        shipping_price = float(data['shippingPrice'])
        total_price = float(data['totalPrice'])

        order = Order.objects.create(
            user=user,
            paymentMethod=data['paymentMethod'],
            taxPrice=tax_price,
            shippingPrice=shipping_price,
            totalPrice=total_price
        )

        shipping_data = data.get('shippingAddress')
        if not shipping_data:
            return Response({'detail': 'Shipping address missing'}, status=400)

        ShippingAddress.objects.create(
            order=order,
            address=shipping_data['address'],
            city=shipping_data['city'],
            postalCode=shipping_data['postalCode'],
            country=shipping_data['country'],
        ) 

        for i in orderItems:
            try:
                product = Product.objects.get(id=i['product'])
                quantity = int(i['qty'])
                price = float(i['price'])
            except (KeyError, ValueError, Product.DoesNotExist) as e:
                return Response({'detail': f'Invalid order item: {str(e)}'}, status=400)

            item = OrderItem.objects.create(
                product=product,
                order=order,
                name=product.name,
                quantity=quantity,
                price=price,
                image=product.image.url,
            )

            product.countInStock -= item.quantity
            product.save()

        serializer = OrderSerializer(order, many=False)
        return Response(serializer.data)

    except Exception as e:
        print('ERROR CREATING ORDER:', str(e))
        return Response({'detail': f'Server error: {str(e)}'}, status=500)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    user = request.user
    orders = user.order_set.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAdminUser])
def getOrders(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):

    user = request.user

    try:
        order = Order.objects.get(id=pk)
        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data)
        else:
            Response({'detail':'Not authorized to view this order'},
                 status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'detail': 'Order does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request, pk):
    order = Order.objects.get(id=pk)

    order.isPaid = True
    order.paidAt = datetime.now()
    order.save()
    
    return Response('Order was Paid')

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateOrderToDelivered(request, pk):
    order = Order.objects.get(id=pk)

    order.isDelivered = True
    order.deliveredAt = datetime.now()
    order.save()
    
    return Response('Order was delivered')