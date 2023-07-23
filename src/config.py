import os
import pathlib
from dotenv import load_dotenv
from pydantic import BaseSettings

# load environment variables from .env.
from utilities import go_n_levels_up

load_dotenv()


class Settings(BaseSettings):
    # integrations
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
    AWS_ACCESS_KEY_ID: str = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY: str = os.getenv('AWS_SECRET_ACCESS_KEY')
    S3_REGION_NAME: str = os.getenv('S3_REGION_NAME')
    S3_BUCKET_NAME: str = os.getenv('S3_BUCKET_NAME')
    S3_ENDPOINT_URL: str = os.getenv('S3_ENDPOINT_URL')
    S3_BUCKET_FOLDER: str = os.getenv('S3_BUCKET_FOLDER')

    # llm
    LLM_PATH: str = os.getenv('LLM_PATH')

    # index path
    INDEX_PATH: str = os.path.join(go_n_levels_up(os.path.abspath(__file__), 2), 'data', 'embeddings')




