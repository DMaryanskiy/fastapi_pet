import bcrypt
from sqlalchemy.orm import Session

from . import models, schemas

# Lists CRUDL
def get_list(db: Session, list_id: int):
    return db.query(models.ToDoList).filter(models.ToDoList.id == list_id).first()

def get_lists(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.ToDoList).offset(skip).limit(limit).all()

def create_list(db: Session, list_schema: schemas.ListCreate, user_id: int):
    db_list = models.ToDoList(**list_schema.dict(), user=user_id)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list

# Tasks CRUDL
def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Task).offset(skip).limit(limit).all()

def create_task(db: Session, task: schemas.TaskCreate, list_id: int):
    db_task = models.Task(**task.dict(), list_owner=list_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Users CRUDL
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    db_user = models.User(
        firstname = user.firstname,
        lastname = user.lastname,
        username = user.username,
        hashed_password = hashed_password.decode()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
