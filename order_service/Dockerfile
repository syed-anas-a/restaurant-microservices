FROM python:3.14-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY ./remote-auth ./remote-auth
COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./order_service .

EXPOSE 8004

CMD ["python", "manage.py", "runserver", "0.0.0.0:8004"]