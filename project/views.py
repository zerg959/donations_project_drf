from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema

from django.contrib.auth.models import User
from project.models import Collect, Payment
from project.serializers import (
    CollectSerializer, 
    PaymentSerializer,
    UserSerializer,
    UserRegistrationSerializer
    )

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
            request_body=UserRegistrationSerializer,
            responses={201: UserSerializer}
    )
    @action(detail=False,methods=['post'], url_path='register')
    def register(self, request):
        """
        New user registration endpoint.
        """
        serializer=UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Registration successful.",
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh_token": str(refresh),
                    "access_token": str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @swagger_auto_schema(
            responses={201: UserSerializer},
    )
    @action(detail=False, methods=['get'], url_path="profile", permission_classes=[IsAuthenticated])
    def profile(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Check permissions: only author or SU can edit and delete.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class CollectViewSet(viewsets.ModelViewSet):
    queryset = Collect.objects.all()
    serializer_class = CollectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='feed')
    def payments_feed(self, request, pk=None):
        collect = self.get_object()
        payments = collect.payments.all().order_by('-timestamp')
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data )
    
    @action(detail=True, methods=['post'], url_path='pay')
    def pay(self, request, pk=None):
        collect = self.get_object()
        amount = request.data.get('amount')
        try:
            amount = float(amount)
            if amount < 0:
                raise ValueError
            
        except(ValueError, TypeError):
            return Response(
                {"err": "Amount must be a positive integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
        payment = collect.add_payment(request.user, amount)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.select_related('user').all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
