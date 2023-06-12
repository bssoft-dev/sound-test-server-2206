import motor.motor_asyncio
from fastapi_users.db import MongoDBUserDatabase

from models import UserDB
from environment import database_url, db_name

client = motor.motor_asyncio.AsyncIOMotorClient(
    database_url, uuidRepresentation="standard"
)
db = client[db_name]
userT = db["users"]


# Database connect for fastapi-users
async def get_user_db():
    yield MongoDBUserDatabase(UserDB, userT)