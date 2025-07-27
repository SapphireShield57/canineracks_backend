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

            PROFILE_MAP = {
                "PUPPY": "PU",
                "ADULT": "AD",
                "SENIOR": "SE",
                "SMALL": "SM",
                "MEDIUM": "ME",
                "LARGE": "LA",
                "GIANT": "GI",
                "SHORT-HAIRED": "SH",
                "LONG-HAIRED": "LH",
                "HYPOALLERGENIC": "HY",
                "WORKING / SERVICE DOGS": "WS",
                "COMPANION DOGS": "CO",
                "NONE": "NO",
                "BRACHYCEPHALIC (SHORT-NOSED)": "BR",
                "JOINT AND MOBILITY ISSUES": "JM",
                "ALLERGIES AND SENSITIVITIES": "AS",
            }

            ALL_EQUIV = {
                'PU': ['LI'],
                'AD': ['LI'],
                'SE': ['LI'],
                'SH': ['CT'],
                'LH': ['CT'],
                'HY': ['CT'],
                'WS': ['LS'],
                'CO': ['LS'],
                'LS': ['LS'],
                'NO': ['NOBRJMAS'],
                'BR': ['NOBRJMAS'],
                'JM': ['NOBRJMAS'],
                'AS': ['NOBRJMAS'],
                'SM': ['BS'],
                'ME': ['BS'],
                'LA': ['BS'],
                'GI': ['BS'],
            }

            # Map dog profile values to short codes
            life_stage = PROFILE_MAP.get(dog.life_stage.upper().strip(), "")
            size = PROFILE_MAP.get(dog.size.upper().strip(), "")
            coat_type = PROFILE_MAP.get(dog.coat_type.upper().strip(), "")
            role = PROFILE_MAP.get(dog.role.upper().strip(), "")
            health_codes = [
                PROFILE_MAP.get(h.strip().upper(), "") for h in dog.health_considerations.split(',') if h.strip()
            ]

            all_products = Product.objects.filter(main_category__in=MAIN_CATEGORIES)
            recommended = []

            def matches(value, segment, all_equiv):
                if value in segment:
                    return True
                if segment in all_equiv.get(value, []):
                    return True
                if value in all_equiv:
                    for alt in all_equiv[value]:
                        if alt in segment:
                            return True
                return False

            for product in all_products:
                code = product.product_code.upper().replace(' ', '')
                segments = code.split('-')
                if len(segments) < 5:
                    continue  # skip malformed codes

                life_stage_seg = segments[0]
                size_seg = segments[1]
                coat_seg = segments[2]
                role_seg = segments[3]
                health_seg = segments[4]

                if (
                    matches(life_stage, life_stage_seg, ALL_EQUIV) and
                    matches(size, size_seg, ALL_EQUIV) and
                    matches(coat_type, coat_seg, ALL_EQUIV) and
                    matches(role, role_seg, ALL_EQUIV) and
                    any(matches(hc, health_seg, ALL_EQUIV) for hc in health_codes)
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
