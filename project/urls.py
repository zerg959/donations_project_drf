from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from project.views import CollectViewSet, PaymentViewSet, AuthViewSet

router = DefaultRouter()
router.register(r'collections', CollectViewSet, basename='collection')
router.register(r'payments', PaymentViewSet, basename='payment')


auth_router = DefaultRouter()
auth_router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(auth_router.urls)),
    path('token/', TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
]
