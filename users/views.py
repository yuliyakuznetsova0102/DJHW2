from rest_framework import viewsets
from .models import Payment, User
from users.serializers import PaymentSerializer, UserSerializer, UserRegistrationSerializer
from .filters import PaymentFilter
from django_filters import rest_framework as filters
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.permissions import AllowAny


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]