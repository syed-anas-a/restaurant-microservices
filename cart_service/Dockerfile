FROM python:3.14-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY ./remote-auth ./remote-auth
COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY --chmod=755 ./docker/entrypoint.sh /usr/local/bin/docker-entrypoint.sh

COPY ./cart_service .

EXPOSE 8003

ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8003"]