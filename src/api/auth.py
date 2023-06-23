import os
from fastapi import HTTPException
from typing import Dict, List, Optional

import boto3
import requests
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, jwk, JWTError
from jose.utils import base64url_decode

# this basically specifies the url for getting tokens and will be used to inject the token in the function that
# retrieves the current user
from starlette import status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

client = boto3.client('cognito-idp', region_name='eu-north-1')


async def get_current_user(token: str = Depends(oauth2_scheme)):
    print(token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = client.get_user(AccessToken=token)
    except JWTError:
        raise credentials_exception
    return user
