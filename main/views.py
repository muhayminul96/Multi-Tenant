from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, TokenSerializer, VendorSerializer, ProductSerializer, OrderSerializer
from .permissions import IsAdminOrVendor, IsVendorOrReadOnly, IsCustomer
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Product, Order, OrderItem

# User
User = get_user_model()

class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            token_data = {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
            serializer = TokenSerializer(token_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # This will blacklist the refresh token
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
# End User

# vendor Start

class VendorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(role='vendor')
    serializer_class = VendorSerializer
    permission_classes = [IsAdminOrVendor]
# end vendor

# product start

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['price', 'created_at']
    filterset_fields = ['vendor']
    permission_classes = [permissions.IsAuthenticated, IsVendorOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.role != 'vendor':
            raise permissions.PermissionDenied("Only vendors can create products.")
        serializer.save(vendor=self.request.user)

    def get_queryset(self):
        if self.request.user.role == 'vendor':
            return self.queryset.filter(vendor=self.request.user)
        return self.queryset
# end product


# order start

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'customer':
            return self.queryset.filter(customer=self.request.user)
        elif self.request.user.role == 'vendor':
            # Orders containing products belonging to the vendor
            return self.queryset.filter(items__product__vendor=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        if self.request.user.role != 'customer':
            raise permissions.PermissionDenied("Only customers can place orders.")
        serializer.save(customer=self.request.user)

# end Order
