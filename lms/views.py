from rest_framework import viewsets, generics, status
from .models import Course, Lesson, Subscription, Payment
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .paginators import LessonPaginator, CoursePaginator
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .services import stripe
from .services.stripe import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_checkout_session
)
from django.urls import reverse
from django.conf import settings
from .tasks import send_course_update_notification


class CourseViewSet(viewsets.ModelViewSet):
    @extend_schema(
        description='Получить список всех курсов с пагинацией',
        parameters=[
            OpenApiParameter(name='page', description='Номер страницы', type=int),
            OpenApiParameter(name='page_size', description='Количество элементов на странице', type=int),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsOwner | IsModerator]
        return [permission() for permission in self.permission_classes]

    def perform_update(self, serializer):
        instance = serializer.save()
        send_course_update_notification.delay(instance.id)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsOwner | IsModerator]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_id = request.data.get('course')
        if not course_id:
            return Response(
                {"error": "Не указан курс"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {"error": "Курс не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            course=course
        )

        if created:
            return Response(
                {"message": "Подписка добавлена"},
                status=status.HTTP_201_CREATED
            )
        else:
            subscription.delete()
            return Response(
                {"message": "Подписка удалена"},
                status=status.HTTP_200_OK
            )


class CreatePaymentView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')
        lesson_id = request.data.get('lesson_id')

        if not (course_id or lesson_id):
            return Response(
                {'error': 'Необходимо указать course_id или lesson_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if course_id:
            item = Course.objects.get(id=course_id)
            item_type = 'course'
        else:
            item = Lesson.objects.get(id=lesson_id)
            item_type = 'lesson'

        product = create_stripe_product(
            name=f'{item_type.title()}: {item.title}',
            description=item.description
        )

        price = create_stripe_price(
            product_id=product.id,
            amount=item.price if hasattr(item, 'price') else 1000
        )

        success_url = request.build_absolute_uri(
            reverse('payment-success')
        )
        cancel_url = request.build_absolute_uri(
            reverse('payment-cancel')
        )

        session = create_stripe_checkout_session(
            price_id=price.id,
            success_url=success_url,
            cancel_url=cancel_url
        )

        payment = Payment.objects.create(
            user=user,
            course=item if item_type == 'course' else None,
            lesson=item if item_type == 'lesson' else None,
            amount=price.unit_amount / 100,
            payment_method='transfer',
            stripe_product_id=product.id,
            stripe_price_id=price.id,
            stripe_session_id=session.id,
            payment_url=session.url,
            is_paid=False
        )

        return Response({
            'payment_url': session.url,
            'payment_id': payment.id
        }, status=status.HTTP_201_CREATED)


class PaymentSuccessView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'status': 'Payment successful'})


class PaymentCancelView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'status': 'Payment canceled'})


class StripeWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:

            return Response({'error': str(e)}, status=400)
        except stripe.error.SignatureVerificationError as e:

            return Response({'error': str(e)}, status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            try:
                payment = Payment.objects.get(stripe_session_id=session.id)
                payment.is_paid = True
                payment.save()

            except Payment.DoesNotExist:
                return Response({'error': 'Payment not found'}, status=404)

        return Response({'status': 'success'}, status=200)
