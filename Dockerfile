FROM python:3.13


ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1


WORKDIR C:\\app


COPY requirements.txt .


RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir psycopg2-binary==2.9.9 && \
    pip install --no-cache-dir -r requirements.txt


COPY . .


EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]