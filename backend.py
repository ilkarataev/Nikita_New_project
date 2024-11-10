import re, sys, pytz
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import Flask, render_template, request, session, redirect, jsonify, url_for,flash
import pymysql
import pymysql.cursors
import logging
from libs import config as configs
from libs import mysql as mysqlfunc
import httpx
from functools import wraps
from flask_cors import CORS
utc_tz = pytz.timezone('UTC')

FREEPIK_API_KEY = configs.freepik_api_token
FREEPIK_API_URL = configs.freepik_api_url
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
app.secret_key = 'xpSm7p5bgJY8rNoBjGWiz5yjxM-NEBlW6SIBI62OkLc='
# Настройка логирования
logging.basicConfig(level=logging.INFO)

# # # Настройка CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Разрешить все источники
#     allow_credentials=True,
#     allow_methods=["*"],  # Разрешить все методы
#     allow_headers=["*"],  # Разрешить все заголовки
# )

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

def login_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        # Check if user is logged in
        if 'email' not in session:
            return redirect(url_for('login')) # User is not logged in; redirect to login page
            
        return func(*args, **kwargs)
    
    return decorator

def set_session(email: str, group: str, remember_me: bool = False) -> None:
    session['email'] = email
    session['group'] = group
    session['balance'] = mysqlfunc.get_balance(email)
    session.permanent = remember_me

@app.route('/')
@login_required
def index():
    # print(f'User data: {session}')
    return render_template('index.html', email=session.get('email'), group=session.get('group'), balance=session.get('balance'))

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
        update_user_passsword_hash(account['email'], ph.hash(password))

    # Set cookie for user session
    set_session(
        email=account['email'], 
        group=account['group'],
        remember_me='remember-me' in request.form
    )
    
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('group') != 'admin':
        return redirect('/')
    if request.method == 'GET':
        return render_template('register.html',)
    
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
    # Get user group from database
    account = mysqlfunc.get_account(email, password)
    if not account:
        return render_template('register.html', error='Error retrieving user information')

    # We can log the user in right away since no email verification
    set_session(email=email, group=account['group'])
    return redirect('/')

@app.route('/api/get_balance', methods=['GET'])
@login_required
def get_balance_route():
    balance = mysqlfunc.get_balance(session['email'])
    return jsonify({'balance': balance})

@app.route('/update_balance', methods=['GET', 'POST'])
@login_required
def update_balance_route():
    if session.get('group') != 'admin':
        flash('You are not authorized to perform this action.')
        return redirect('/')
    
    if request.method == 'GET':
        return render_template('update_balance.html')
    
    email = request.form.get('email')
    amount = float(request.form.get('amount'))
    mysqlfunc.update_balance(email, amount)
    flash(f'Balance updated for {email}')
    return redirect('/update_balance')

@app.route('/api/get_emails', methods=['GET'])
@login_required
def get_emails():
    if session.get('group') != 'admin':
        return jsonify([])  # Возвращаем пустой список, если пользователь не администратор

    emails = mysqlfunc.get_all_emails()
    return jsonify(emails)

@app.route('/api/get_prices', methods=['GET'])
def get_prices():
    prices = mysqlfunc.get_all_prices()
    return jsonify(prices)

@app.route('/api/get_price', methods=['GET'])
def get_price():
    original_width = int(request.args.get('original_width'))
    original_height = int(request.args.get('original_height'))
    scale_factor = request.args.get('scale_factor')
    price = mysqlfunc.get_upscale_price(original_width, original_height, scale_factor)
    if price is not None:
        return jsonify({'price': price})
    else:
        return jsonify({'error': 'Цена не найдена'}), 404

@app.route("/api/image-upscaler", methods=["POST"])
def upscale_image():
    try:
        scale_factor=2
        request_data = request.get_json()

        original_width = request_data.pop('original_width', None)
        original_height = request_data.pop('original_height', None)
        image_price = request_data.pop('image_price', None)
        if request_data.get(scale_factor) is not None:
            scale_factor = request_data.get('scale_factor')

        # # Получение цены обработки изображения
        price = mysqlfunc.get_upscale_price(original_width, original_height, scale_factor)
        if price is None:
            return jsonify({"detail": "Цена обработки изображения не найдена"}), 400

        # Проверка баланса пользователя
        email = session.get('email')
        balance = mysqlfunc.get_balance(email)
        if balance < price:
            return jsonify({"detail": "Недостаточно средств на балансе"}), 400
        # logger.info("Data: %s", request_data)
        # Отправка запроса на обработку изображения
        response = httpx.post(
            FREEPIK_API_URL,
            json=request_data,
            headers={
                'Content-Type': 'application/json',
                'x-freepik-api-key': FREEPIK_API_KEY
            }
        )
        # logger.info("Request payload: %s", response)
        if response.status_code == 200:
            response_data = response.json()
            task_id = response_data.get('data').get('task_id')

            # Сохранение запроса в базу данных
            mysqlfunc.save_api_request(email, original_width, original_height, scale_factor, image_price, task_id)

            return jsonify({"task_id": task_id})
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
            status = response_data.get('data').get('status')
            if status == 'COMPLETED':
                # Вычитание стоимости из баланса пользователя
                email = session.get('email')
                price = mysqlfunc.get_price_by_task_id(task_id)
                mysqlfunc.update_balance(email, -price)
                image_url = response_data.get('data').get('generated')[0]
                return jsonify({'status': status, 'image_url': f'/api/download_image?url={image_url}'})
            else:
                return jsonify(response_data.get('data'))
        else:
            return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error("Error: %s", str(e))
        return jsonify({"detail": "Ошибка обработки запроса"}), 422

@app.route('/api/download_image', methods=['GET'])
def download_image():
    url = request.args.get('url')
    if not url:
        return jsonify({"detail": "URL не указан"}), 400

    try:
        response = httpx.get(url)
        headers = {key: value for key, value in response.headers.items() if key.lower() in ['content-type', 'content-length']}
        return response.content, response.status_code, headers
    except Exception as e:
        logger.error("Error: %s", str(e))
        return jsonify({"detail": "Ошибка при запросе к прокси"}), 500


if __name__ == '__main__':
    app.run(debug=True)