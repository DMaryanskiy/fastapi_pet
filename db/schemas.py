import datetime as dt

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    hashed_password: str
    disabled: bool

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class TaskBase(BaseModel):
    task: str
    time: dt.time
    description: str = ""
    done: bool = False


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int

    class Config:
        orm_mode = True


class ListBase(BaseModel):
    name: str


class ListCreate(ListBase):
    pass


class List(ListBase):
    id: int
    tasks: list[Task] = []
    user_id: int

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
