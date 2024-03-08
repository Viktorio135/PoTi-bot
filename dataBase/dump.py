import json
import time
import logging
import schedule
import subprocess
import os

from dotenv import load_dotenv

load_dotenv()

user_bd = os.getenv('USER_BD')
password = os.getenv('PASSWORD')
host = os.getenv('HOST')
database = os.getenv('DATABASE')


def dump_dict_of_profiles(dict_of_profiles):
    try:
        with open('static/backups/dump.json', 'w') as file:
            json.dump(dict_of_profiles, file)
        logging.info('Dump dict_of_profiles')
        return 1
    except Exception as e:
        logging.error(f'Ошибка дампа dict_of_profiles: {e}')
        return 0

def backup_bd():
    try:
        print('adsasd')
        backup_path = 'static/backups/database.sql'
        os.environ['MYSQL_PWD'] = password
        subprocess.run(['mysqldump', '-u', user_bd, database, '--result-file', backup_path])
        logging.info('Dump database')
    except Exception as e:
        logging.error(f'Ошибка дамба базы данных: {e}')
    finally:
        del os.environ['MYSQL_PWD']



def scheduled_backup_dict_of_profiles(dict_of_profiles):
    schedule.every(0.5).minutes.do(dump_dict_of_profiles, dict_of_profiles)
    schedule.every(0.1).minutes.do(backup_bd)
    while True:
        schedule.run_pending()
        time.sleep(1)