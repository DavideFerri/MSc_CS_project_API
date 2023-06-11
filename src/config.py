import os
import pathlib
from dotenv import load_dotenv
from pydantic import BaseSettings

# load environment variables from .env.
load_dotenv()


class Settings(BaseSettings):

    # db
    MONGO_DB_URL: str = os.getenv('MONGO_DB_URL')
    MONGO_DB_ENV: str = os.getenv('MONGO_DB_ENV')

    # auth
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ALGORITHM: str = os.getenv('ALGORITHM')


