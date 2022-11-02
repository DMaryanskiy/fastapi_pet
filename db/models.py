from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Time, Table

from .database import metadata

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("firstname", String, index=True),
    Column("lastname", String, index=True),
    Column("email", String, unique=True, index=True),
    Column("hashed_password", String, index=True),
    Column("disabled", Boolean)
)

task = Table(
    "task",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("task", String, index=True),
    Column("time", Time),
    Column("description", Text, index=True),
    Column("done", Boolean),

    Column("list_id", Integer, ForeignKey("todolist.id"))
)

todolist = Table(
    "todolist",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, index=True),

    Column("user_id", Integer, ForeignKey("users.id"))
)
