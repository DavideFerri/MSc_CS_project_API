import boto3
from fastapi import Depends, FastAPI, HTTPException, status, concurrency
from functools import lru_cache

from fastapi.security import OAuth2PasswordRequestForm
from src.api.auth import client, get_current_user
from src.api.models.user import JWTBearer
from src.config import Settings


# load settings - see https://fastapi.tiangolo.com/advanced/settings/
@lru_cache
def get_settings():
    return Settings()


def create_app() -> FastAPI:
    # initialize app with settings
    app = FastAPI()
    # get settings
    settings = get_settings()

    # welcome page
    @app.get("/")
    async def root():
        return {"message": "Welcome to the API!"}

    # authenticate users and generate tokens
    @app.post("/token")
    async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
        # get token from cognito
        response = await concurrency.run_in_threadpool(
            client.initiate_auth,
            ClientId=settings.aws_cognito_app_client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": form_data.username,
                "PASSWORD": form_data.password,
            },
        )
        return response["AuthenticationResult"]["AccessToken"]

    # get list of portfolios belonging to user
    @app.get("/users/me/portfolios")
    async def read_all_my_portfolios_names(current_user: str = Depends(get_current_user)):
        return None

    return app
