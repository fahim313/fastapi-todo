from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Annotated 
from database import SessionLocal
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer 
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

bcrypt_context = CryptContext(
     schemes=["bcrypt"],
    deprecated="auto"
)
OAuth2_bearer = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class CreateUsers(BaseModel):
    email: str
    username: str
    firstname: str
    lastname: str
    password: str
    role: str
    phone_number: str


# Request body for the password-change endpoint.
# User must send both the old (current) password and the new one.
class PasswordChange(BaseModel):
    old_password: str
    new_password: str


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hash_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(OAuth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        role: str = payload.get('role')

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user"
            )
        return {'username': username, 'id': user_id, 'role': role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user"
        )


user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/createuser")
def create_users(db: db_dependency, new_user: CreateUsers):
    user_model = Users(
        email=new_user.email,
        username=new_user.username,
        firstname=new_user.firstname,
        lastname=new_user.lastname,
        hash_password=bcrypt_context.hash(new_user.password),
        is_active=True,
        role=new_user.role,
        phone_number=new_user.phone_number
    )
    db.add(user_model)
    db.commit()

    return JSONResponse(
        status_code=201,
        content={"message": "User created successfully"}
    )


@router.post("/login")
def login_user(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password is incorrect"
        )

    token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=20)
    )
    return {"access_token": token, "token_type": "bearer"}


# PUT /change-password
# Lets the logged-in user change their own password.
# Steps:
# 1. Check the user is logged in (valid token).
# 2. Verify the "old_password" they sent actually matches what's in the DB.
# 3. If it matches, hash the "new_password" and save it.
# This extra verification step is important — without it, anyone holding
# a stolen token could change the password without knowing the real one.

@router.put("/change-password")
def change_password(
    user: user_dependency,
    db: db_dependency,
    password_data: PasswordChange
):
    if user is None:
        raise HTTPException(status_code=401, detail="Failed Authentication")

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt_context.verify(password_data.old_password, user_model.hash_password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    user_model.hash_password = bcrypt_context.hash(password_data.new_password)

    db.commit()

    return JSONResponse(
        status_code=200,
        content={"message": "Password changed successfully"}
    )