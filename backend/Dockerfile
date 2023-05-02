FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir 
COPY backend/ .
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000" ]
ONBUILD RUN python manage.py migrate
ONBUILD RUN python manage.py collectstatic --noinput
