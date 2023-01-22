# TODOList API
It's my pet project where I decided to use FastAPI as framework to learn it and some other technologies. During its development I've learned:
1. FastAPI.
2. Async Web Development.
3. Async PostgreSQL connection.
4. Alembic (learned in the final stage and couldb't use it properly but however practiced it).

I haven't implemented all I want because couldn't find any information how to implement dropdown lists in API :)

## Installation
1. Clone repository.
2. Create virtual environment `python -m venv venv`.
3. Activate it `source ./venv/Scripts/activate` in Windows.
4. Install requirements using `pip install -r requirements.txt`.
5. Create `.env` file and put there:
```
DB_URL="postgresql+asyncpg://<your_data>".
SECRET_KEY (generate it for bcrypt).
ALGORITHM to encode.
ACCESS_TOKEN_EXPIRE_MINUTES.
EMAIL_HOST address of email which will send notifications.
EMAIL_PASSWORD its password.
```
6. Launch app `uvicorn main:app --reload`.
7. Go to the `http://127.0.0.1/docs` to check all paths.
