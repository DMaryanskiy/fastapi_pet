import os

import databases
import sqlalchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.curdir, '.env'))

SQLACHEMY_DATABASE_URL = f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"

database = databases.Database(SQLACHEMY_DATABASE_URL)
metadata = sqlalchemy.MetaData()
engine = create_engine(SQLACHEMY_DATABASE_URL)
metadata.create_all(engine)
