from django.core.cache import cache

from django.contrib.auth.models import User

from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        AllowAny,
                                        IsAuthenticated
                                        )
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from project.models import Collect, Payment
from project.serializers import (
    CollectSerializer,
    PaymentSerializer,
    UserSerializer,
    UserRegistrationSerializer
    )
# Cache key
COLLECT_LIST_CACHE_KEY = "collect_list_v1"
# Cache lifetime param (sec)
CACHE_LIFETIME_PERIOD_SEC = 900


def get_collect_feed_cache_key(collect_id):
    "Return cache id"
    return f"collect_feed_{collect_id}"


class AuthViewSet(viewsets.ViewSet):
    """
    User registration and authorization representation.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
            request_body=UserRegistrationSerializer,
            responses={201: UserSerializer}
    )
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        """
        New user registration endpoint.
        """
        serializer = UserRegistrationSerializer(data=request.data)
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
    @action(detail=False,
            methods=['get'],
            url_path="profile",
            permission_classes=[IsAuthenticated]
            )
    def profile(self, request):
        """
        User profile endpoint.
        """
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
    """
    Collect viewset after serialization.
    """
    queryset = Collect.objects.all()
    serializer_class = CollectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        """
        Overrided default method list: add cache.
        """
        cached_data = cache.get(COLLECT_LIST_CACHE_KEY)
        if cached_data is not None:
            print('!!!!!!Read from cache')
            return Response(cached_data)
        print('!!!!!Read from BD')
        response = super().list(request, *args, **kwargs)
        cache.set(COLLECT_LIST_CACHE_KEY,
                  response.data,
                  timeout=CACHE_LIFETIME_PERIOD_SEC)
        print('!!!!!!!!!DATA SAVE to DB')
        return response

    def perform_create(self, serializer):
        """
        Create new collect.
        Author = the user who created the collect.
        Clear cache after new collect created
        """
        obj = serializer.save(author=self.request.user)
        cache.delete(COLLECT_LIST_CACHE_KEY)
        return obj

    def perform_update(self, serializer):
        """
        Overrided default update method: delete cache if obj updated.
        """
        obj = serializer.save()
        cache.delete(COLLECT_LIST_CACHE_KEY)
        cache.delete(f"collect_id_{obj.id}")
        return obj

    def perform_destroy(self, instance):
        """
        Overrided default destroy method: clear cache before obj deleted.
        """
        cache.delete(COLLECT_LIST_CACHE_KEY)
        cache.delete(f"collect_detail_{instance.id}")
        cache.delete(get_collect_feed_cache_key(instance.id))
        instance.delete()

    @action(detail=True, methods=['get'], url_path='feed')
    def payments_feed(self, request, pk=None):
        """
        Payment feed with cache.
        """
        collect = self.get_object()
        cache_key = get_collect_feed_cache_key(collect.id)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        payments = collect.payments.all().order_by('-timestamp')
        serializer = PaymentSerializer(payments, many=True)
        data = serializer.data
        cache.set(cache_key,
                  data,
                  timeout=CACHE_LIFETIME_PERIOD_SEC)
        return Response(data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER,
                                         description='Amount')
            },
            required=['amount']
        )
    )
    @action(
        detail=True,
        methods=['post'],
        url_path='pay',
        permission_classes=[IsAuthenticated]
        )
    def pay(self, request, pk=None):
        """
        New single payment.
        """
        collect = self.get_object()
        amount = request.data.get('amount')
        try:
            amount = float(amount)
            if amount < 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"err": "Amount must be a positive integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
        payment = collect.add_payment(request.user, amount)
        serializer = PaymentSerializer(payment)

        cache.delete(COLLECT_LIST_CACHE_KEY)
        cache.delete(get_collect_feed_cache_key(collect.id))

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Single payment representation serialized class.
    """
    queryset = Payment.objects.select_related('user').all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        cached_data = cache.get("payment_list")
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set("payment_list",
                  response.data,
                  timeout=CACHE_LIFETIME_PERIOD_SEC)
        return response
