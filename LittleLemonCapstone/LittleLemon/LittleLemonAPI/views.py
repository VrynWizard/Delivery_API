
from django.contrib.auth.models import User, Group


from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, NotFound
from django.shortcuts import get_object_or_404
from .models import MenuItem, Order, Cart, OrderItem
from .serializers import MenuItemSerializer, OrderSerializer, CartSerializer, OrderItemSerializer, UserSerializer
from django.contrib.auth.models import User, Group

# Order views for Customers
class CustomerOrderList(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        orders = self.get_queryset()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        total = sum(item.price for item in cart_items)
        order = Order.objects.create(user=request.user, total=total, status=False)
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price,
            )
        
        cart_items.delete()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CustomerOrderDetail(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        order = get_object_or_404(self.get_queryset(), pk=kwargs['pk'])
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs['pk'], user=request.user)
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs['pk'], user=request.user)
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

# Order management for Manager and Delivery Crew
class ManagerOrderList(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]

class ManagerOrderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs['pk'])
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs['pk'])
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs['pk'])
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs['pk'])
        order.delete()
        return Response(status=status.HTTP_200_OK)

class DeliveryCrewOrderList(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(delivery_crew=self.request.user)

class DeliveryCrewOrderDetail(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs['orderId'], delivery_crew=request.user)
        order.status = request.data.get('status', order.status)
        order.save()
        return Response(status=status.HTTP_200_OK)

# MenuItem views
class MenuItemList(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        items = self.get_queryset()
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Manager').exists():
            raise PermissionDenied("You do not have permission to perform this action.")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MenuItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        item = get_object_or_404(MenuItem, pk=kwargs['pk'])
        serializer = self.get_serializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Manager').exists():
            raise PermissionDenied("You do not have permission to perform this action.")
        item = get_object_or_404(MenuItem, pk=kwargs['pk'])
        serializer = self.get_serializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Manager').exists():
            raise PermissionDenied("You do not have permission to perform this action.")
        item = get_object_or_404(MenuItem, pk=kwargs['pk'])
        item.delete()
        return Response(status=status.HTTP_200_OK)

# User group management views
class ManagerUsers(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=request.data['user_id'])
        managers = Group.objects.get(name='Manager')
        managers.user_set.add(user)
        return Response(status=status.HTTP_201_CREATED)

class ManagerUserDetail(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, userId, *args, **kwargs):
        user = get_object_or_404(User, pk=userId)
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)
        return Response(status=status.HTTP_200_OK)

class DeliveryCrewUsers(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Delivery crew')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=request.data['user_id'])
        delivery_crew = Group.objects.get(name='Delivery crew')
        delivery_crew.user_set.add(user)
        return Response(status=status.HTTP_201_CREATED)

class DeliveryCrewUserDetail(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, userId, *args, **kwargs):
        user = get_object_or_404(User, pk=userId)
        delivery_crew = Group.objects.get(name='Delivery crew')
        delivery_crew.user_set.remove(user)
        return Response(status=status.HTTP_200_OK)

# Cart management views
class CartMenuItems(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_200_OK)
