from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from src.api.auth import authenticate_user, create_access_token, get_current_active_user
from src.config import Settings
from src.database import get_dbs
from src.api.models.user import UserModel, TokenModel
from functools import lru_cache
import boto3


# load settings - see https://fastapi.tiangolo.com/advanced/settings/
@lru_cache
def get_settings():
    return Settings()


# create app
def create_app() -> FastAPI:
    # initialize app with settings
    app = FastAPI()

    # initialize db
    db = get_dbs()

    # welcome page
    @app.get("/")
    async def root():
        return {"message": "Welcome to the API!"}

    # authenticate users and generate tokens
    @app.post("/token", response_model=TokenModel)
    async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                     settings: Settings = Depends(get_settings)):
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return TokenModel(username=user.username, access_token=access_token, token_type="bearer")

    @app.get("/users/me/documents", response_model=list[str])
    async def get_docs_list(settings: Settings = Depends(get_settings),
                            current_user: UserModel = Depends(get_current_active_user)):
        # Let's use Amazon S3
        s3 = boto3.resource("s3")

        # Print out bucket names
        for bucket in s3.buckets.all():
            print(bucket.name)

    return app
