FROM python:3.11-slim-buster

COPY requirements.txt /tmp/

RUN apt-get update && apt-get install -y libpq-dev gcc python-dev supervisor nginx openssl curl && \
  mkdir -p /etc/nginx/ssl/ && \
  openssl req \
            -x509 \
            -subj "/C=US/ST=Massachusetts/L=Cambridge/O=Dis" \
            -nodes \
            -days 365 \
            -newkey rsa:2048 \
            -keyout /etc/nginx/ssl/nginx.key \
            -out /etc/nginx/ssl/nginx.cert && \
  chmod -R 755 /etc/nginx/ssl/ && \
  pip install --upgrade pip && \
  pip install --upgrade --force-reinstall -r /tmp/requirements.txt -i https://pypi.org/simple/ --extra-index-url https://test.pypi.org/simple/

RUN useradd --create-home appuser
WORKDIR /home/appuser

COPY --chown=appuser ./ .

# Update permissions for the appuser user and group
COPY change_id.sh /root/change_id.sh
RUN chmod 755 /root/change_id.sh && \
  /root/change_id.sh -u 55020 -g 1636

USER appuser

CMD ["celery", "-A", "tasks.tasks", "worker", "--loglevel=info", "--queues", "email-notifier"]
