from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import exception_handler
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q

from .models import Product, StockHistory, Order
from .serializers import ProductSerializer, StockHistorySerializer, OrderSerializer
from users.models import DogProfile
from rest_framework.exceptions import ValidationError


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        instance = serializer.save()
        StockHistory.objects.create(
            product=instance,
            action='in',
            quantity_changed=instance.quantity
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_quantity = instance.quantity

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        new_quantity = serializer.validated_data.get('quantity', old_quantity)
        if new_quantity != old_quantity:
            quantity_diff = new_quantity - old_quantity
            action_type = "in" if quantity_diff > 0 else "out"
            StockHistory.objects.create(
                product=instance,
                action=action_type,
                quantity_changed=abs(quantity_diff)
            )

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        product = self.get_object()
        history = StockHistory.objects.filter(product=product).order_by('-timestamp')
        serializer = StockHistorySerializer(history, many=True)
        return Response(serializer.data)


MAIN_CATEGORIES = ['Food', 'Treat', 'Health', 'Grooming', 'Wellness']


class RecommendationView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        try:
            dog = DogProfile.objects.get(owner=self.request.user)
            dog_attrs = [
                dog.life_stage.upper(),            # e.g. 'PU'
                dog.size.upper(),                 # e.g. 'SM'
                dog.coat_type.upper(),            # e.g. 'SH'
                dog.role.upper(),                 # e.g. 'CO'
            ]
            health_codes = [h.strip().upper() for h in dog.health_considerations.split(',')]
            dog_attrs.extend(health_codes)
    
            all_products = Product.objects.filter(main_category__in=MAIN_CATEGORIES)
            recommended = []
    
            for product in all_products:
                code = product.product_code.upper().replace(' ', '')
                segments = code.split('-')
    
                if len(segments) < 5:
                    continue  # Ignore improperly formatted products
    
                life_stage_seg = segments[0]  # e.g. 'PUAD'
                size_seg = segments[1]       # e.g. 'BSSM'
                coat_seg = segments[2]       # e.g. 'HYSH'
                role_seg = segments[3]       # e.g. 'CO'
                health_seg = segments[4]     # e.g. 'NOBRJM'
    
                if (
                    dog.life_stage in life_stage_seg and
                    dog.size in size_seg and
                    dog.coat_type in coat_seg and
                    dog.role in role_seg and
                    any(h in health_seg for h in health_codes)
                ):
                    recommended.append(product)
    
            return recommended
    
        except DogProfile.DoesNotExist:
            return Product.objects.none()

# ============================
# Custom Exception Handler
# ============================

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        print("\n==== DRF Validation Error Debug ====")
        print(response.data)
        print("====================================\n")
    return response


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
