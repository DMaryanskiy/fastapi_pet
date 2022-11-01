import datetime as dt
from pydantic import BaseModel

class TaskBase(BaseModel):
    task: str
    time: dt.time
    description: str | None = None
    done: bool = False


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    list_id: int

    class Config:
        orm_mode = True


class ListBase(BaseModel):
    name: str


class ListCreate(ListBase):
    user: int


class List(ListBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class UserBase(BaseModel):
    firstname: str
    lastname: str
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    hashed_password: str

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
