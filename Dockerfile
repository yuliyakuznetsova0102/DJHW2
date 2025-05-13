# Используем официальный образ Python с конкретной версией
FROM python:3.9-slim

# Устанавливаем системные зависимости для psycopg2 и чистки
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Сначала копируем только requirements.txt для кэширования слоя
COPY requirements.txt ./

# Устанавливаем зависимости (с явным указанием psycopg2-binary)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt psycopg2-binary==2.9.9

# Копируем остальные файлы проекта в контейнер
COPY . .

# Открываем порт 8000 для взаимодействия с приложением
EXPOSE 8000

# Определяем команду для запуска приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]