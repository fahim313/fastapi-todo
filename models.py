# Todo table / SQLAlchemy model

from sqlalchemy import Column, Integer, String, Boolean
from database import Base


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    priority = Column(Integer, nullable=False)
    complete = Column(Boolean, default=False)