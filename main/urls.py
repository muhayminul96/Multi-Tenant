from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, OrderViewSet, VendorViewSet, RegisterAPIView, LoginAPIView, LogoutAPIView

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'vendors', VendorViewSet)

urlpatterns = [
    path('api/register/', RegisterAPIView.as_view(), name='register'),
    path('api/token/', LoginAPIView.as_view(), name='login'),
    path('api/token/refresh/', LogoutAPIView.as_view(), name='logout'),
    path('api/', include(router.urls)),
]
