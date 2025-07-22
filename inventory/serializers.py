from rest_framework import serializers
from .models import Product, StockHistory, Order, OrderItem

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']



class StockHistorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = StockHistory
        fields = ['id', 'product', 'product_name', 'action', 'quantity_changed', 'timestamp']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'created_at', 'items']
        read_only_fields = ['id', 'created_at', 'customer']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        order = Order.objects.create(customer=user, **validated_data)

        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            # Update stock
            if product.quantity < quantity:
                raise serializers.ValidationError(f"Not enough stock for {product.name}")
            product.quantity -= quantity
            product.save()

            # Log stock history
            StockHistory.objects.create(
                product=product,
                action='out',
                quantity_changed=quantity
            )

            OrderItem.objects.create(order=order, product=product, quantity=quantity)

        # Send confirmation email
        from django.core.mail import send_mail
        from django.conf import settings

        product_lines = [
            f"{item_data['quantity']} x {item_data['product'].name}"
            for item_data in items_data
        ]
        message_body = f"Thank you for your order!\n\nOrder Number: {order.id}\n\nItems:\n" + "\n".join(product_lines)

        send_mail(
            subject='Your CanineRacks Order Confirmation',
            message=message_body,
            from_email='canineracks@gmail.com',
            recipient_list=[user.email],
            fail_silently=False,
        )

        return order
