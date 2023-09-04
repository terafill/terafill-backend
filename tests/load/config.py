import os

from dotenv import load_dotenv

ENV = os.getenv("ENV", "LOCAL")

env2config = {
    "DEV": ".env.dev",
    "PROD": ".env.prod",
    "LOCAL": ".env.local",
}

if int(os.getenv("LOAD_ENV_FROM_FILE", 1)):
    load_dotenv(env2config[ENV])

# Database configuration
MYSQL_HOST = os.environ["MYSQL_HOST"]
MYSQL_PORT = os.environ["MYSQL_PORT"]
MYSQL_USER = os.environ["MYSQL_USER"]
MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]
MYSQL_DB = os.environ["MYSQL_DB"]

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

HOST = os.environ["HOST"]

print("Database URL: ", DATABASE_URL)
print("HOST: ", HOST)
