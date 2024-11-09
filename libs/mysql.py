# from msilib.schema import Error
import pymysql,sys
import pymysql.cursors
from libs import config as configs
def getConnection():
    try:
        connection = pymysql.connect(host=configs.db_host,
                                    user=configs.db_user,
                                    password=configs.db_password,
                                    database=configs.db_name,
                                    port=int(configs.db_port),
                                    cursorclass=pymysql.cursors.DictCursor,
                                    autocommit=True)
        connection.ping(reconnect=True)
        # print("MySQL Connection Sucessfull!")
        return connection
    except Exception as err:
        try:
            connection = pymysql.connect(host='localhost',
                                    user=configs.db_user,
                                    password=configs.db_password,
                                    database=configs.db_name,
                                    port=int(configs.db_port),
                                    cursorclass=pymysql.cursors.DictCursor,
                                    autocommit=True)
            connection.ping(reconnect=True)
            # print("MySQL Connection Sucessfull!")
            return connection
        except Exception as err:
            print(f"MySQL Connection Failed !{err}")
            sys.exit(1)
        # print(f"MySQL Connection Failed !{err}")
        # sys.exit(1)

def get_account(email, password):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = 'SELECT * FROM users WHERE email = %s'
                cursor.execute(sql, (email))
                result=cursor.fetchone()
                return result
    except Exception as e:
        print(f'В функции mysql get_account что-то пошло не так: {e}')


def check_email(email):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = 'SELECT email FROM users WHERE email = %s'
                cursor.execute(sql, (email))
                result=cursor.fetchone()
                if result != None:
                    return True
                else:
                    return False
    except Exception as e:
        print(f'В функции mysql check_email что-то пошло не так: {e}')

def register_user(email, password, reg_date):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql =  'INSERT INTO users(email, password, balance, reg_date) VALUES (%s, %s,%s, %s)'
                cursor.execute(sql, (email, password, 0, reg_date))
                result=cursor.fetchone()
                if result != None:
                    return True
                else:
                    return False
    except Exception as e:
        print(f'В функции mysql register_user что-то пошло не так: {e}')


def update_user_passsword_hash(email, password):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = 'UPDATE users SET password = %s WHERE email = %s'
                cursor.execute(sql, (password, email ))
                result=cursor.fetchone()
                if result != None:
                    return True
                else:
                    return False
    except Exception as e:
        print(f'В функции mysql update_user_passsword_hash что-то пошло не так: {e}')


def get_balance(email):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = 'SELECT balance FROM users WHERE email = %s'
                cursor.execute(sql, (email,))
                result = cursor.fetchone()
                if result:
                    return result['balance']
                else:
                    return 0.0
    except Exception as e:
        print(f'В функции mysql get_balance что-то пошло не так: {e}')
        return 0.0

def update_balance(email, amount):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = 'UPDATE users SET balance = balance + %s WHERE email = %s'
                cursor.execute(sql, (amount, email))
                connection.commit()
                return True
    except Exception as e:
        print(f'В функции mysql update_balance что-то пошло не так: {e}')
        return False

def get_all_emails():
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = 'SELECT email FROM users'
                cursor.execute(sql)
                result = cursor.fetchall()
                return [row['email'] for row in result]
    except Exception as e:
        print(f'В функции mysql get_all_emails что-то пошло не так: {e}')
        return []

def get_upscale_price(original_width, original_height, scale_factor):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = '''
                SELECT price FROM image_upscale_prices
                WHERE original_width >= %s AND original_height >= %s
                AND scale_factor = %s
                ORDER BY original_width ASC, original_height ASC
                LIMIT 1
                '''
                cursor.execute(sql, (original_width, original_height, scale_factor))
                result = cursor.fetchone()
                if result:
                    return result['price']
                else:
                    return None
    except Exception as e:
        print(f'В функции mysql get_upscale_price что-то пошло не так: {e}')
        return None

def save_api_request(email, original_width, original_height, scale_factor, price, task_id):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = '''
                INSERT INTO api_requests (user_id, request_date, original_width, original_height, scale_factor, price, task_id)
                VALUES ((SELECT id FROM users WHERE email = %s), NOW(), %s, %s, %s, %s, %s)
                '''
                cursor.execute(sql, (email, original_width, original_height, scale_factor, price, task_id))
                connection.commit()
    except Exception as e:
        print(f'В функции mysql save_api_request что-то пошло не так: {e}')

def get_price_by_task_id(task_id):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = '''
                SELECT price FROM api_requests
                WHERE task_id = %s
                '''
                cursor.execute(sql, (task_id,))
                result = cursor.fetchone()
                if result:
                    return result['price']
                else:
                    return None
    except Exception as e:
        print(f'В функции mysql get_price_by_task_id что-то пошло не так: {e}')
        return None

def get_all_prices():
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = 'SELECT * FROM image_upscale_prices'
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
    except Exception as e:
        print(f'В функции mysql get_all_prices что-то пошло не так: {e}')
        return []