from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from .models import Product, StockHistory
from .serializers import ProductSerializer, StockHistorySerializer
from users.models import DogProfile
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication 
from rest_framework.views import exception_handler
from rest_framework import status

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_quantity = instance.quantity

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Check for quantity change and create stock history
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


class RecommendationView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication] 

    def get_queryset(self):
        try:
            dog = DogProfile.objects.get(owner=self.request.user)
            filters = Q(life_stage_code__in=[dog.life_stage, 'LI']) & \
                      Q(breed_size_code__in=[dog.size, 'BS']) & \
                      Q(coat_type_code__in=[dog.coat_type, 'CT']) & \
                      Q(lifestyle_code__in=[dog.role, 'LS']) & \
                      Q(health_code__in=[dog.health_considerations, 'NO'])

            return Product.objects.filter(filters)
        except DogProfile.DoesNotExist:
            return Product.objects.none()

# ============================
# Debug Exception Handler
# ============================

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        print("\n==== DRF Validation Error Debug ====")
        print(response.data)
        print("====================================\n")
    return response
