from django.core.management.base import BaseCommand
from users.models import Payment, User
from lms.models import Course, Lesson
from datetime import datetime

class Command(BaseCommand):
    help = 'Populates the Payment model with sample data'

    def handle(self, *args, **kwargs):
        user1 = User.objects.get(id=1)
        user2 = User.objects.get(id=2)
        course1 = Course.objects.get(id=1)
        lesson1 = Lesson.objects.get(id=1)

        Payment.objects.create(
            user=user1,
            payment_date=datetime.now(),
            paid_course=course1,
            amount=100.00,
            payment_method='cash'
        )
        Payment.objects.create(
            user=user2,
            payment_date=datetime.now(),
            paid_lesson=lesson1,
            amount=50.00,
            payment_method='transfer'
        )

        self.stdout.write(self.style.SUCCESS('Payments created successfully'))