from fastapi import FastAPI,Depends,HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import models
from models import Todos
from database import engine,SessionLocal
from typing import Annotated,Optional
from pydantic import BaseModel,Field


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

# create

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
    
    # Update 

@app.put("/update/{todo_id}")
def update_todos(db: db_dependency, todo_id: int, update_todo: TodoUpdate):

    todo = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

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
def delete_todo(db: db_dependency, todo_id: int):

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