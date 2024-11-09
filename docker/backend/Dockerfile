FROM python:alpine3.13
WORKDIR /app
RUN apk update && apk add --no-cache mariadb-client build-base vim && \
    pip install --upgrade pip setuptools gunicorn
COPY requirements.txt ./
RUN	pip install --no-cache-dir -r requirements.txt && \
	rm -rf /tmp/* /var/tmp/*
COPY ./libs/ ./libs
COPY ./*.py ./
COPY ./alembic.ini ./
COPY ./frontend ./frontend
COPY ./migrations ./migrations
COPY ./docker/backend/entrypoint.sh /entrypoint.sh
# RUN chmod +x docker/python/startup.sh
ENTRYPOINT [ "/bin/sh", "/entrypoint.sh"]