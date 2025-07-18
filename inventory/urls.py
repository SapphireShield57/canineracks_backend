from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, RecommendationView

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('recommendations/', RecommendationView.as_view(), name='product-recommendations'),
]
