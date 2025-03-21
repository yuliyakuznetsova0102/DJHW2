from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, UserViewSet, UserRegistrationView

router = DefaultRouter()
router.register(r'payments', PaymentViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='register'),
]
