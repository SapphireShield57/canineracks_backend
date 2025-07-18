from rest_framework import serializers
from .models import Product, StockHistory

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['created_at']  # Only created_at should be read-only

class StockHistorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = StockHistory
        fields = ['id', 'product', 'product_name', 'action', 'quantity_changed', 'timestamp']
