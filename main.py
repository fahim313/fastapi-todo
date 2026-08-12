from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy.orm import Session
import models
from models import Todos
from database import engine,SessionLocal
from typing import Annotated
from pydantic import BaseModel,Field


app = FastAPI()


class TODO(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=5, max_length=200)
    priority: int = Field(ge=1, le=5)
    complete: bool
    

# Create database tables
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]

# Get all 
@app.get("/")
def get_todos(db:db_dependency):
   return db.query(Todos).all()

# Get specific
@app.get("/todo/{todo_id}")
def get_specific_todo(db: db_dependency, todo_id: int):

    todo = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    return todo

@app.post("/create", status_code=201)
def create_todos(db: db_dependency, new_todo: TODO):
    todo_model = Todos(**new_todo.model_dump())

    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)

    return {
        "message": "Todo successfully added",
        "todo": todo_model
    }