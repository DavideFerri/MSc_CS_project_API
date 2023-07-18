from typing import Union
from datetime import datetime, timedelta
from jose import JWTError, jwt
from src.api.models.user import UserModel, UserInDB, TokenDataModel
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.database import get_dbs
from src.config import Settings

# get settings
settings = Settings()

# get db
db = get_dbs()

# -------------------------------------- utilities --------------------------------------#
# create pwd context to expose hashing functionality
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# utility functions
def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db, username: str):
    if db["users"].count_documents({'username': username}, limit=1) > 0:
        user_dict = db["users"].find_one({'username': username})
        return UserInDB(**user_dict)

# -------------------------------------- key functions --------------------------------------#


# this basically specifies the url for getting tokens and will be used to inject the token in the function that
# retrieves the current user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# this function verifies pw and returns user if user exists and password is correct
def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# this function creates the jwt itself
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# this function gets the token, decodes it, and returns user record
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenDataModel(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# same as get_current_user, but also checks if user is active
async def get_current_active_user(current_user: UserModel = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user