from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from project.models import Collect, Payment
from project.serializers import CollectSerializer, PaymentSerializer, UserSerializer

class CollectViewSet(viewsets.ModelViewSet):
    queryset = Collect.objects.all()
    serializer_class = CollectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

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
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]