from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Annotated 
from database import SessionLocal
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer 
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from router.auth import get_current_user
from models import Todos


router = APIRouter()



def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/admin/todo")
def read_all(user: user_dependency, db: db_dependency):

    if user is None:
        raise HTTPException(status_code=401, detail="Failed Authentication")

    if user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")

    return db.query(Todos).all()


# admin delete todo

@router.delete("/admin/delete/{todo_id}")
def admin_delete_todo(user: user_dependency, db: db_dependency, todo_id: int):

    if user is None:
        raise HTTPException(status_code=401, detail="Failed Authentication")

    if user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")

    todo = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    db.query(Todos).filter(Todos.id == todo_id).delete()

    db.commit()

    return JSONResponse(
        status_code=200,
        content={"message": "Todo deleted successfully"}
    )