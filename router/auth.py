from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Annotated 
from database import SessionLocal
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm 




router = APIRouter()

bcrypt_context = CryptContext(
     schemes=["bcrypt"],
    deprecated="auto"
)
def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]

class CreateUsers(BaseModel):
    email: str
    username: str
    firstname: str
    lastname: str
    password: str
    role: str

def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        return False
    if not bcrypt_context.verify(password, user.hash_password):
        return False

    return user

@router.post("/createuser")
def create_users(db:db_dependency,new_user: CreateUsers):
    user_model = Users(
        email=new_user.email,
        username=new_user.username,
        firstname=new_user.firstname,
        lastname=new_user.lastname,
        hash_password=bcrypt_context.hash(new_user.password),
        is_active=True,
        role=new_user.role
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

    return {"message": "Authenticated User", "username": user.username}
    