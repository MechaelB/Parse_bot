FROM python:3.11

WORKDIR /app

COPY proxy_worker.py proxy_utils.py ./
RUN pip install celery requests
RUN pip install --upgrade redis kombu


CMD ["celery", "-A", "proxy_worker", "worker", "--loglevel=info"]
