mysql -e "drop database upscale_api"
mysql -e "create database upscale_api"
alembic upgrade head