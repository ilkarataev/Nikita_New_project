#!/bin/sh


while ! mysqladmin ping -s -h ${DATABASE_HOST}
do
  sleep 3
  echo "wait mysql"
done
gunicorn -w 4 -b 0.0.0.0:8000 backend:app
# uvicorn backend:app --host 0.0.0.0 --port 8000  # Обновленная команда
# exec python backend.py