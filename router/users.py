from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from models import Users
from database import SessionLocal
from router.auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    firstname: str
    lastname: str
    role: str
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    firstname: Optional[str] = Field(default=None)
    lastname: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)


# GET /users/me
# Returns the profile info of the currently logged-in user (based on their token).
# Password is never returned, since UserResponse doesn't include it.
@router.get("/me", response_model=UserResponse)
def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Failed Authentication")

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user_model


# PUT /users/me
# Lets the logged-in user update their own profile (email, username, name, phone number).
# Only the fields sent in the request body get updated; everything else stays the same.
# Password and role are intentionally excluded here for security reasons.
@router.put("/me")
def update_user(user: user_dependency, db: db_dependency, update_user_data: UserUpdate):
    if user is None:
        raise HTTPException(status_code=401, detail="Failed Authentication")

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = update_user_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(user_model, key, value)

    db.commit()

    return JSONResponse(
        status_code=200,
        content={"message": "Profile updated successfully"}
    )