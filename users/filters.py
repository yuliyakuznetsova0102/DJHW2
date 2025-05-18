import django_filters
from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    paid_course = django_filters.NumberFilter(field_name='paid_course__id')
    paid_lesson = django_filters.NumberFilter(field_name='paid_lesson__id')
    payment_method = django_filters.CharFilter(field_name='payment_method')

    class Meta:
        model = Payment
        fields = ['paid_course', 'paid_lesson', 'payment_method']
