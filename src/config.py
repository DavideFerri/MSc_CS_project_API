import os
import pathlib
from dotenv import load_dotenv
from pydantic import BaseSettings

# load environment variables from .env.
load_dotenv()


class Settings(BaseSettings):
    # src
    # BASE_DIR: str = pathlib.Path(__file__).parent.parent

    # db
    MONGO_DB_URL: str = os.getenv('MONGO_DB_URL')
    MONGO_DB_ENV: str = os.getenv('MONGO_DB_ENV')
    OPERATIONAL_DB_NAME: str = os.getenv('OPERATIONAL_DB_NAME')
    ANALYTICS_DB_NAME: str = os.getenv('ANALYTICS_DB_NAME')

    # auth
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ALGORITHM: str = os.getenv('ALGORITHM')

    # s3
    ACCESS_KEY: str = os.getenv('ACCESS_KEY')
    SECRET_ACCESS_KEY: str = os.getenv('SECRET_ACCESS_KEY')
    S3_BUCKET_NAME: str = os.getenv('S3_BUCKET_NAME')




