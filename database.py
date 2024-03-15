from typing import Optional, List
import motor.motor_asyncio
from pydantic import BaseModel
from fastapi_users.db import MongoDBUserDatabase

import psycopg2
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from datetime import datetime
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

def get_current_time():
    return datetime.now().strftime('%y%m%d%H%M%S')

def get_received_time():
    return datetime.now().strftime('%m-%d %H:%M:%S')

def get_url_base():
    return [f"{get_current_time()}-ori_ch0.wav"]

class SoundModel(BaseModel):
    id : str
    recKey : Optional[str]
    receivedTime : Optional[str]
    oriStatus : Optional[str] = 'Complete'
    oriUrlBase: Optional[List[str]]
    reducStatus : Optional[str] = 'Ready'
    reducUrlBase : Optional[List[str]] = []
    reducprocTime : Optional[str] = ''
    reduc2Status : Optional[str] = 'Ready'
    reduc2UrlBase : Optional[List[str]] = []
    reduc2procTime : Optional[str] = ''
    sepStatus : Optional[str] = 'Ready'
    sepUrlBase : Optional[List[str]] = []
    sepprocTime : Optional[str] = ''
    duration : Optional[str]
    memo : Optional[str] = ''

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

    def read_all(self):
        query = self.session.query(self.table)  # 테이블에 대한 쿼리 생성
        query = query.order_by(desc(self.table.columns.recKey))
        rows = query.all()
        result = [row._asdict() for row in rows]
        return result
    
    def update(self, recKey: str, data: SoundModel):
        # 데이터를 딕셔너리 형태로 변환합니다.
        # exclude_unset는 값이 설정되지 않은 필드들은 딕셔너리에서 제외하는 옵션
        update_data = data.dict(exclude_unset=True)
        self.session.execute(
            self.table.update().where(self.table.c.recKey == recKey).values(**update_data)
        )
        self.session.commit()


    def delete(self, recKey: str) -> bool:
        # 추출한 recKey를 사용하여 해당 데이터를 삭제합니다.
        self.session.execute(
            self.table.delete().where(self.table.c.recKey == recKey)
        )
        # 변경 사항을 데이터베이스에 반영하기 위해 commit을 호출합니다.
        self.session.commit()
        return 'file delete'
