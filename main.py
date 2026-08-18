from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import models
from models import Todos, Users
from database import engine, SessionLocal
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from router import auth, admin, users
from router.auth import get_current_user


app = FastAPI()


class TODO(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=5, max_length=200)
    priority: int = Field(ge=1, le=5)
    complete: bool


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=50)
    description: Optional[str] = Field(default=None, max_length=100)
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    complete: Optional[bool] = Field(default=None)


# Create database tables
models.Base.metadata.create_all(bind=engine)

# Connect routers with the main app
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)


def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


# Get all 
@app.get("/")
def get_todos(user: user_dependency, db: db_dependency):
   return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


# Get specific
@app.get("/todo/{todo_id}")
def get_specific_todo(user: user_dependency, db: db_dependency, todo_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="Faild Authenticaiton")

    todo = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).filter(Todos.id == todo_id).first()

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    return todo


# create
@app.post("/create", status_code=201)
def create_todos(user: user_dependency, db: db_dependency, new_todo: TODO):
    if user is None:
        raise HTTPException(status_code=401, detail="Failed Authentication")

    todo_model = Todos(**new_todo.model_dump(), owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)

    return {
        "message": "Todo successfully added",
        "todo": todo_model
    }


# Update 
@app.put("/update/{todo_id}")
def update_todos(user: user_dependency, db: db_dependency, todo_id: int, update_todo: TodoUpdate):
    if user is None:
        raise HTTPException(status_code=401, detail="Failed Authentication")

    todo = db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id == todo_id).first()

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    update_data = update_todo.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(todo, key, value)

    db.commit()

    return JSONResponse(
        status_code=200,
        content={"message": "Todo updated successfully"}
    )


# Delete 
@app.delete("/delete/{todo_id}")
def delete_todo(user: user_dependency, db: db_dependency, todo_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="Failed Authentication")

    todo = db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id == todo_id).first()

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id == todo_id).delete()

    db.commit()

    return JSONResponse(
        status_code=200,
        content={"message": "Todo deleted successfully"}
    )