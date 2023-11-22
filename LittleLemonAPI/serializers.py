from rest_framework import serializers
from .models import MenuItem, Cart, Order, OrderItem

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']

class CartSerializer(serializers.ModelSerializer):
    menuitem = serializers.SlugRelatedField(
        queryset=MenuItem.objects.all(),
        slug_field='title'
    )
     
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity', 'unit_price', 'price']

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = serializers.SlugRelatedField(
        queryset=MenuItem.objects.all(),
        slug_field='title'
    )
    
    class Meta:
        model = OrderItem
        fields = ['menuitem', 'quantity', 'unit_price', 'price']

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    delivery_crew = serializers.StringRelatedField(read_only=True)
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    total = serializers.DecimalField(read_only=True, max_digits=6, decimal_places=2)
    date = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id','user', 'delivery_crew', 'status', 'total', 'date', 'items']