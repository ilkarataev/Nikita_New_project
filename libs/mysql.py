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
        print(f"MySQL Connection Failed !{err}")
        sys.exit(1)

def get_account(email, password):
    try:
        with getConnection() as connection:
            with connection.cursor() as cursor:
                sql = 'SELECT id, email, password FROM users WHERE email = %s'
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