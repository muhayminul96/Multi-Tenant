from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Product, OrderItem, Order

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'vendor', 'name', 'price', 'stock', 'is_active', 'created_at']
        read_only_fields = ['vendor', 'created_at']
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id','items', 'created_at', 'is_active']
        read_only_fields = ['customer', 'created_at']

    def create(self, validated_data):
        order_items_data = validated_data.pop('items')
        print(validated_data)
        order = Order.objects.create(**validated_data)

        # Reduce stock for each ordered product
        for item_data in order_items_data:

            product = Product.objects.get(id=item_data['product'].id)  # Get the product
            if product.stock >= item_data['quantity']:
                product.stock -= item_data['quantity']  # Reduce stock
                product.save()
                OrderItem.objects.create(order=order, product=item_data['product'], quantity=item_data['quantity'])  # Create OrderItem
            else:
                raise serializers.ValidationError(f"Not enough stock for {product.name}.")  # Handle insufficient stock

        return order
