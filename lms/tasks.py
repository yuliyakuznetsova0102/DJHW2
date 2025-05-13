from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Course, Subscription
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_course_update_notification(self, course_id):
    try:
        course = Course.objects.get(id=course_id)
        subscriptions = Subscription.objects.filter(course=course).select_related('user')

        if course.updated_at >= timezone.now() - timedelta(hours=4):
            logger.info(f"Course {course_id} was updated recently, skipping notifications")
            return "No notifications sent - course was updated recently"

        sent_count = 0
        for subscription in subscriptions:
            try:
                send_mail(
                    subject=f'Обновление курса "{course.title}"',
                    message=f'Курс "{course.title}" был обновлен. Посмотрите новые материалы!\n\n'
                            f'Ссылка на курс: {settings.BASE_URL}/courses/{course.id}/',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscription.user.email],
                    fail_silently=False,
                )
                sent_count += 1
                logger.debug(f"Sent notification to {subscription.user.email}")
            except Exception as e:
                logger.error(f"Failed to send email to {subscription.user.email}: {str(e)}")
                continue

        logger.info(f"Successfully sent {sent_count}/{subscriptions.count()} notifications for course {course_id}")
        return f"Sent notifications to {sent_count} users"

    except Course.DoesNotExist as exc:
        logger.error(f"Course {course_id} not found")
        raise self.retry(exc=exc, countdown=60)
    except Exception as exc:
        logger.error(f"Error in send_course_update_notification: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


User = get_user_model()


@shared_task
def check_inactive_users():
    one_month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(
        last_login__lt=one_month_ago,
        is_active=True
    )

    count = inactive_users.count()
    inactive_users.update(is_active=False)

    return f"Blocked {count} inactive users"
