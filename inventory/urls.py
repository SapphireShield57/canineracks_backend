from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, RecommendationView, OrderCreateView

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('recommendations/', RecommendationView.as_view(), name='product-recommendations'),
    path('order/create/', OrderCreateView.as_view(), name='order-create'),
]
