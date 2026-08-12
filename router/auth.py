from fastapi import APIRouter
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Annotated 
from database import SessionLocal
from fastapi import Depends
from fastapi.responses import JSONResponse

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