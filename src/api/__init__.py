import io
import os
from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, File
from fastapi.openapi.models import Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from starlette.responses import StreamingResponse

from src.api.auth import authenticate_user, create_access_token, get_current_active_user
from src.api.models.general import BinaryResponseModel
from src.api.s3 import S3Connector
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

    # initialize S3Connector
    s3connector = S3Connector()

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
        return s3connector.get_object_ids()

    @app.get("/users/me/documents/{document_name}", response_model=bytes)
    async def get_doc(document_name: str,
                      folder_path: str = 'K-10_docs',
                      settings: Settings = Depends(get_settings),
                      current_user: UserModel = Depends(get_current_active_user)):
        document_id = f"{folder_path}/{document_name}"
        file_content = s3connector.get_object(document_id)

        # Use StreamingResponse to directly stream the file content as a raw response
        return StreamingResponse(io.BytesIO(file_content), media_type='application/octet-stream',
                                 headers={"Content-Disposition": f"attachment; filename={document_name}"})

    @app.post("/users/me/documents")
    async def upload_doc(file: UploadFile = File(...),
                         folder_path: str = 'K-10_docs',
                         settings: Settings = Depends(get_settings),
                         current_user: UserModel = Depends(get_current_active_user)):
        # check if user is allowed to upload documents
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not allowed to upload documents",
                headers={"WWW-Authenticate": "Bearer"},
            )
        document_id = f"{folder_path}/{file.filename}"
        s3connector.add_doc(file, document_id)
        return {"message": f"Document {file.filename} successfully uploaded to S3!"}

    return app

    @app.post("/users/me/chatbot")
    async def chatbot(message: str,
                        settings: Settings = Depends(get_settings),
                        current_user: UserModel = Depends(get_current_active_user)):
        # initialize chatbot instance
        chatbot = Chatbot()
