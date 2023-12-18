import os
# print(os.environ)

mail_id = os.getenv('MAIL_ID', '')
if mail_id == '':
    raise Exception('MAIL_ID is not set')

mail_passwd = os.getenv('MAIL_PASSWORD', '')
if mail_passwd == '':
    raise Exception('MAIL_PASSWORD is not set')

database_url = os.getenv('DATABASE_URL', '')
if database_url == '':
    raise Exception('DATABASE_URL is not set')

db_name = os.getenv('DB', '')
if db_name == '':
    raise Exception('DB is not set. Please use docker run with -e DB=<db_name>')

hyper_name = os.getenv('HYPER_NAME', '')
if hyper_name == '':
    raise Exception('HYPER_NAME is not set')

postgres_db_name = os.getenv('POSTGRES_DB', '')
if postgres_db_name == '':
    raise Exception('POSTGRES_DB is not set. Please use docker run with -e POSTGRES_DB=<postgres_db_name>')

postgres_url = os.getenv('POSTGRES_URL', '')
if postgres_url == '':
    raise Exception('POSTGRES_URL is not set')