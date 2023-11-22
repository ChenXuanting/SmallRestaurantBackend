from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from django.db.models import Sum, F
from django.db import transaction
from django.utils import timezone

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, generics, status

from djoser.serializers import UserSerializer

from .serializers import (MenuItemSerializer, CartSerializer,
                          OrderSerializer, OrderItemSerializer)
from .models import MenuItem, Cart, Order, OrderItem

class IsManagerOrReadOnly(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.method == 'GET':
            return True
        else:
            return request.user.groups.filter(name='Manager').exists()

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user:
            return request.user.groups.filter(name='Manager').exists()
        return False

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='Manager').exists() or request.user.groups.filter(name='delivery crew').exists():
            return False
        return request.user.is_authenticated
    
def CorrectGroupName(group_name):
    corrected_group_name = ''
    if group_name == 'manager':
            corrected_group_name = 'Manager'
    elif group_name == 'delivery-crew':
            corrected_group_name = 'delivery crew'
    return corrected_group_name
    
class UserMe(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class MenuItemList(generics.ListCreateAPIView):
    permission_classes = [IsManagerOrReadOnly]
    def get(self, request, format=None):
        items = MenuItem.objects.all()
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    
    def put(self, request, *args, **kwargs):
        return HttpResponse('PUT operation is not valid for this url.')
    
    def patch(self, request, *args, **kwargs):
        return HttpResponse('PATCH operation is not valid for this url.')
    
    def delete(self, request, *args, **kwargs):
        return HttpResponse('DELETE operation is not valid for this url.')

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsManagerOrReadOnly]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
class GroupUsersView(APIView):
    permission_classes = [IsManager]
    serializer_class = UserSerializer
    
    def get(self, request, group_name):
        group_name = CorrectGroupName(group_name)
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        members = group.user_set.all()
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, group_name):
        username = request.data.get('username')
        group_name = CorrectGroupName(group_name)
        try:
            user = User.objects.get(username=username)
            group = Group.objects.get(name=group_name)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        group.user_set.add(user)
        if group_name == 'Manager':
            user.is_staff = True
            user.save()
        return Response(status=status.HTTP_201_CREATED)
    
class SingleGroupUserView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsManager]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        user = get_object_or_404(User, id=id)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        group_name = kwargs.get('group_name')
        group_name = CorrectGroupName(group_name)
        
        user = get_object_or_404(User, id=id)
        group = Group.objects.get(name=group_name)
    
        user.groups.remove(group)
        return Response(status=status.HTTP_200_OK)
    
class CartAPIView(generics.GenericAPIView):
    permission_classes = [IsCustomer]
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)

    def get(self, request):
        queryset = self.get_queryset()
        serializer = CartSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        user = request.user
        menuitem_title = data.get('menuitem')
        
        # Lookup the MenuItem by title
        try:
            menuitem = MenuItem.objects.get(title=menuitem_title)
        except MenuItem.DoesNotExist:
            return Response({"error": "MenuItem not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate the total price
        quantity = int(data.get('quantity'))
        unit_price = menuitem.price
        total_price = unit_price * quantity
        
        cart_item, created = Cart.objects.get_or_create(user=user, menuitem=menuitem, defaults={'quantity': 0, 'unit_price': unit_price, 'price': 0})

        if not created:
            cart_item.quantity = F('quantity') + quantity
            cart_item.price = F('price') + total_price
            cart_item.save(update_fields=['quantity', 'price'])
        else:
            cart_item.quantity = quantity
            cart_item.price = total_price
            cart_item.save()
        
        cart_item.refresh_from_db()

        serializer = CartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        queryset = self.get_queryset()
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CustomerOrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='delivery crew').exists():
            return Order.objects.filter(delivery_crew=user)
        return Order.objects.filter(user=user)

    @transaction.atomic  # ensure this operation is atomic
    def create(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name='Manager').exists() or user.groups.filter(name='delivery crew').exists():
            return Response({"detail": "You cannot perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        order = Order.objects.create(user=user, date=timezone.now())
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order, 
                menuitem=item.menuitem, 
                quantity=item.quantity, 
                unit_price=item.unit_price, 
                price=item.price
            )
        
        order.total = order.orderitem_set.aggregate(total=Sum(F('price'))).get('total') or 0
        order.save()
        
        cart_items.delete()
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class SingleCustomerOrderView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='delivery crew').exists():
            return Order.objects.filter(delivery_crew=user)
        return Order.objects.filter(user=user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if user.groups.filter(name='Manager').exists():
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            # receive the username from request data
            delivery_crew_username = request.data.get('delivery_crew')
            if delivery_crew_username is not None:
                try:
                    delivery_crew_user = User.objects.get(username=delivery_crew_username)
                    # check if the user is in the delivery crew group
                    if not delivery_crew_user.groups.filter(name='delivery crew').exists():
                        return Response({"error": "This user is not a delivery crew member."}, status=status.HTTP_400_BAD_REQUEST)
                    serializer.validated_data['delivery_crew'] = delivery_crew_user
                except User.DoesNotExist:
                    return Response({"error": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)
            self.perform_update(serializer)
            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            return Response(serializer.data)
        elif user.groups.filter(name='delivery crew').exists():
            if 'status' in request.data.keys():
                instance.status = request.data.get('status')
                instance.save()
                return Response(OrderSerializer(instance).data)
            return Response({"detail": "You are not allowed to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return Response({"detail": "You are not allowed to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            super().destroy(request, *args, **kwargs)
            return Response({"detail": "Order deleted successfully."}, status=status.HTTP_200_OK)
        return Response({"detail": "You do not have permission to delete this order."}, status=status.HTTP_403_FORBIDDEN)
