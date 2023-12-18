from typing import Optional
import motor.motor_asyncio
from pydantic import BaseModel
from fastapi_users.db import MongoDBUserDatabase

import psycopg2
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy import asc, desc

from models import UserDB
from environment import database_url, db_name, postgres_db_name, postgres_url

client = motor.motor_asyncio.AsyncIOMotorClient(
    database_url, uuidRepresentation="standard"
)
db = client[db_name]
userT = db["users"]

# Database connect for fastapi-users
async def get_user_db():
    yield MongoDBUserDatabase(UserDB, userT)

connection_string = "{}/{}".format(postgres_url, postgres_db_name)

class PostgresDB():
    def __init__(self):
        self.db = psycopg2.connect(connection_string)
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()
        self.cursor.close()

    def execute(self,query,args={}):
        self.cursor.execute(query,args)
        row = self.cursor.fetchall()
        return row

    def commit(self):
        self.cursor.commit()

class SoundModel(BaseModel):
    id : str
    recKey : Optional[str]
    receivedTime : Optional[str]
    oriStatus : Optional[str]
    oriUrlBase: Optional[list]
    reducStatus : Optional[str]
    reducUrlBase : Optional[list] 
    reducprocTime : Optional[str]
    reduc2Status : Optional[str]
    reduc2UrlBase : Optional[list]
    reduc2procTime : Optional[str]
    sepStatus : Optional[str]
    sepUrlBase : Optional[list]
    sepprocTime : Optional[str]
    duration : Optional[str] 
    memo : Optional[str]

class SoundData():
    def __init__(self):
        engine = create_engine(connection_string)
        Session = sessionmaker(bind=engine)
        self.session = Session()

        metadata = MetaData()
        self.table = Table('sound', metadata, autoload_with=engine)

    def insert(self, data: SoundModel):
        self.new_entry = data.dict()
        self.session.execute(self.table.insert(), self.new_entry)
        self.session.commit()
    
    def read(self):
        query = self.session.query(self.table)  # 테이블에 대한 쿼리 생성
        query = query.order_by(desc(self.table.columns.recKey))
        rows = query.all()
        result = [row._asdict() for row in rows]
        return result

