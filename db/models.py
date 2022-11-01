from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Time, LargeBinary

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, index=True)
    lastname = Column(String, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, index=True)


class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, index=True)
    time = Column(Time)
    description = Column(Text, index=True)
    done = Column(Boolean)

    list_id = Column(Integer, ForeignKey("todolist.id"))


class ToDoList(Base):
    __tablename__ = "todolist"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"))
