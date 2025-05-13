from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CourseViewSet, LessonListCreateView, LessonRetrieveUpdateDestroyView,
                    SubscriptionAPIView, CreatePaymentView, PaymentSuccessView,
                    PaymentCancelView, StripeWebhookView)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    path('', include(router.urls)),
    path('lessons/', LessonListCreateView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonRetrieveUpdateDestroyView.as_view(), name='lesson-detail'),
    path('subscriptions/', SubscriptionAPIView.as_view(), name='subscription-list'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('api/payments/create/', CreatePaymentView.as_view(), name='create-payment'),
    path('api/payments/success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('api/payments/cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
]
