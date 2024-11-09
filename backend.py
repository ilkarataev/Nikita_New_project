import re, sys, pytz
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import Flask, render_template, request, session, redirect, jsonify, url_for
import pymysql
import pymysql.cursors
import logging
from libs import config as configs
# from utils import login_required, set_session
from libs import mysql as mysqlfunc
import httpx
from functools import wraps

utc_tz = pytz.timezone('UTC')

FREEPIK_API_KEY = configs.freepik_api_token
FREEPIK_API_URL = configs.freepik_api_url
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
app.secret_key = 'xpSm7p5bgJY8rNoBjGWiz5yjxM-NEBlW6SIBI62OkLc='
# Настройка логирования
logging.basicConfig(level=logging.INFO)

# # Настройка CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Разрешить все источники
#     allow_credentials=True,
#     allow_methods=["*"],  # Разрешить все методы
#     allow_headers=["*"],  # Разрешить все заголовки
# )

def login_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        # Check if user is logged in
        if 'email' not in session:
            return redirect(url_for('login')) # User is not logged in; redirect to login page
            
        return func(*args, **kwargs)
    
    return decorator

def set_session(email: str, remember_me: bool = False) -> None:
    session['email'] = email
    session.permanent = remember_me

@app.route('/')
@login_required
def index():
    print(f'User data: {session}')
    return render_template('index.html', email=session.get('email'))

@app.route('/logout')
def logout():
    session.clear()
    session.permanent = False
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    # Set data to variables
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Attempt to query associated user data
    account= mysqlfunc.get_account(email, password)

    if not account: 
        return render_template('login.html', error='Email does not exist')

    # Verify password
    try:
        ph = PasswordHasher()
        ph.verify(account['password'], password)
    except VerifyMismatchError:
        return render_template('login.html', error='Incorrect password')

    # Check if password hash needs to be updated
    if ph.check_needs_rehash(account['password']):
        query = 'UPDATE users SET password = %s WHERE email = %s'
        params = (ph.hash(password), account['email'])
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute(query, params)
        connection.close()

    # Set cookie for user session
    set_session(
        email=account['email'], 
        remember_me='remember-me' in request.form
    )
    
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    # Store data to variables 
    password = request.form.get('password')
    confirm_password = request.form.get('confirm-password')
    email = request.form.get('email')

    # Verify data
    if len(password) < 8:
        return render_template('register.html', error='Your password must be 8 or more characters')
    if password != confirm_password:
        return render_template('register.html', error='Passwords do not match')
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return render_template('register.html', error='Invalid email address')

    # Check if email already exists
    result= mysqlfunc.check_email(email)
    if result:
        return render_template('register.html', error='Email already exists')

    # Create password hash
    pw = PasswordHasher()
    hashed_password = pw.hash(password)
    current_time_utc = pytz.datetime.datetime.now(utc_tz)
    time_now=current_time_utc.strftime('%Y-%m-%d %H:%M:%S')
    reg_date=pytz.datetime.datetime.now(utc_tz).strftime('%Y-%m-%d %H:%M:%S')
    mysqlfunc.register_user(email, hashed_password, reg_date)
    # We can log the user in right away since no email verification
    set_session(email=email)
    return redirect('/')






@app.route("/api/image-upscaler", methods=["POST"])
def upscale_image():
    try:
        request_data = request.get_json()
        logger.info("Request payload: %s", request_data)
        # image_request = ImageRequest(**request_data)
        response = httpx.post(
            FREEPIK_API_URL,
            json=request_data,
            headers={
                'Content-Type': 'application/json',
                'x-freepik-api-key': FREEPIK_API_KEY
            }
        )
        logger.info("Request payload: %s", response)
        if response.status_code == 200:
            response_data = response.json()
            return jsonify(response_data.get('data'))
        else:
            return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error("Error: %s", str(e))
        return jsonify({"detail": "Ошибка обработки запроса"}), 422

@app.route("/api/image-upscaler/<task_id>", methods=["GET"])
def check_status(task_id: str):
    try:
        response = httpx.get(f"{FREEPIK_API_URL}/{task_id}", headers={
            'x-freepik-api-key': FREEPIK_API_KEY
        })
        if response.status_code == 200:
            response_data = response.json()
            return jsonify(response_data.get('data'))
        else:
            return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error("Error: %s", str(e))
        return jsonify({"detail": "Ошибка обработки запроса"}), 422


if __name__ == '__main__':
    app.run(debug=True)