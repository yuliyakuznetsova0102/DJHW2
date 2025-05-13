from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Lesson, Course, Subscription
from django.contrib.auth import get_user_model


User = get_user_model()


class LessonTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@test.com',
            password='12345'
        )
        self.client.force_authenticate(user=self.user)
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description'
        )
        self.lesson = Lesson.objects.create(
            title='Initial Lesson',
            course=self.course,
            description='Initial Description',
            video_link='https://www.youtube.com/watch?v=initial'
        )

    def test_lesson_create(self):
        url = reverse('lesson-list')
        data = {
            'title': 'New Lesson',
            'course': self.course.id,
            'description': 'New Description',
            'video_link': 'https://www.youtube.com/watch?v=xyz789',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Lesson.objects.filter(title='New Lesson').exists())

    def test_lesson_youtube_validation(self):
        url = reverse('lesson-list')
        data = {
            'title': 'Invalid Lesson',
            'course': self.course.id,
            'description': 'Invalid Description',
            'video_link': 'https://vimeo.com/123',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Lesson.objects.filter(title='Invalid Lesson').exists())

    def test_lesson_update(self):
        url = reverse('lesson-detail', args=[self.lesson.id])
        data = {
            'title': 'Updated Lesson',
            'video_link': 'https://www.youtube.com/watch?v=updated',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Lesson')

    def test_lesson_delete(self):
        url = reverse('lesson-detail', args=[self.lesson.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())


class SubscriptionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description'
        )
        self.url = reverse('subscription-list')

    def test_subscription_lifecycle(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {'course': self.course.id},
            format='json'
        )

        if response.status_code != status.HTTP_201_CREATED:
            print(f"Ошибка создания подписки: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('message'), 'Подписка добавлена')

        subscription = Subscription.objects.filter(
            user=self.user,
            course=self.course
        ).first()
        self.assertIsNotNone(subscription)

        response = self.client.post(
            self.url,
            {'course': self.course.id},
            format='json'
        )

        if response.status_code != status.HTTP_200_OK:
            print(f"Ошибка удаления подписки: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'Подписка удалена')
        self.assertFalse(
            Subscription.objects.filter(
                user=self.user,
                course=self.course
            ).exists()
        )

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.url,
            {'course': self.course.id},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
