from django.core.exceptions import ValidationError
from urllib.parse import urlparse

def validate_youtube_url(value):
    parsed_url = urlparse(value)
    if parsed_url.netloc not in ('www.youtube.com', 'youtube.com'):
        raise ValidationError('Допустимы только ссылки на YouTube!')