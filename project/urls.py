from django.urls import path, include
from rest_framework.routers import DefaultRouter
from project.views import CollectViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'collections', CollectViewSet, basename='collection')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]