from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from src.api.auth import authenticate_user, create_access_token, get_current_active_user
from functools import lru_cache
from src.database import get_dbs


def create_app() -> FastAPI:
    # initialize app with settings
    app = FastAPI()

    # initialize db
    db = get_dbs()

    # welcome page
    @app.get("/")
    async def root():
        return {"message": "Welcome to the Financial DialogAI API!"}

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

    # get list of portfolios belonging to user
    @app.get("/users/me/portfolios", response_model=PortfoliosListModel)
    async def read_all_my_portfolios_names(current_user: UserModel = Depends(get_current_active_user)):
        cursor = db["portfolios"].find({'username': current_user.username})
        port_list = [p['name'] for p in cursor]
        return PortfoliosListModel(username=current_user.username, portfolios=port_list)

    # return app
    return app
