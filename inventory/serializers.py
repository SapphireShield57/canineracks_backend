from rest_framework import serializers
from .models import Product, StockHistory

class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']  # prevent overriding timestamps

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url  # Returns Cloudinary URL or default media URL
        return None


class StockHistorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = StockHistory
        fields = ['id', 'product', 'product_name', 'action', 'quantity_changed', 'timestamp']
