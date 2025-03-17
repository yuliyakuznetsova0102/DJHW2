from rest_framework import viewsets
from .models import Payment, User
from users.serializers import PaymentSerializer, UserSerializer
from .filters import PaymentFilter
from django_filters import rest_framework as filters

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer