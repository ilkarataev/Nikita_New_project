#!/bin/sh

while ! mysqladmin ping -s -h${DATABASE_HOST}
do
  sleep 3
  echo "wait until mysql up"
done


case "$1" in
'migrations')
    alembic upgrade head
    ;;
*)
    exec gunicorn -w 4 -b 0.0.0.0:8000 backend:app
    ;;
esac
exit 0


# exec python backend.py