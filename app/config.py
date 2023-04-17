import os

# Database configuration
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'keylance_backend'
MYSQL_PASSWORD = 'Keylance_backend_123'
MYSQL_DB = 'keylance'
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
