from rest_framework import serializers
from .models import Product, StockHistory

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
