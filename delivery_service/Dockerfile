FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY ./remote-auth ./remote-auth
COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./delivery_service .

EXPOSE 8005

CMD ["python", "manage.py", "runserver", "0.0.0.0:8005"]