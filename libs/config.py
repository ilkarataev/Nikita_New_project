import os
from os import environ, path
from dotenv import load_dotenv
 
basedir = path.abspath(path.dirname(__file__))

load_dotenv(path.join(basedir, '../.env'))

# Database config fronm env
db_user = os.environ.get('DATABASE_USERNAME')
db_password = os.environ.get('DATABASE_PASSWORD')
db_host = os.environ.get('DATABASE_HOST')
db_port = os.environ.get('DATABASE_PORT')
db_name = os.environ.get('DATABASE_NAME')
 
db_host_migrations = os.environ.get('DATABASE_HOST_MIGRATIONS')

freepik_api_token = os.environ.get('FREEPIK_API_KEY')
freepik_api_url = os.environ.get('FREEPIK_API_URL')
jwt_secret = os.environ.get('JWT_SECRET')