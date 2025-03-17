from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=255)
    preview = models.ImageField(upload_to='course_previews/', blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    preview = models.ImageField(upload_to='lesson_previews/', blank=True, null=True)
    video_link = models.URLField()
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
