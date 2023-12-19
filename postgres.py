from database import PostgresDB

class CRUD(PostgresDB):
    def createTable(self, schema, table, columns):
        # columns는 (컬럼명, 데이터타입) 튜플의 리스트로 받아옵니다.
        # 예: [("ID", "text"), ("name", "varchar(100)"), ("age", "int")]
        
        # 스키마 생성
        schema_sql = "CREATE SCHEMA IF NOT EXISTS {schema};".format(schema=schema)
        
        # 테이블 생성
        columns_sql = ", ".join(["{} {}".format(name, type) for name, type in columns])
        table_sql = "CREATE TABLE {schema}.{table}({columns});".format(schema=schema, table=table, columns=columns_sql)
        
        try:
            self.cursor.execute(schema_sql)
            self.cursor.execute(table_sql)
            self.db.commit()
        except Exception as e:
            print("Create table error", e)

    def insertDB(self,schema,table,colum,data):
        sql = " INSERT INTO {schema}.{table}({colum}) VALUES ('{data}') ;".format(schema=schema,table=table,colum=colum,data=data)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e :
            print(" insert DB err ",e) 
    
    def readDB(self,schema,table,colum):
        sql = " SELECT {colum} from {schema}.{table}".format(colum=colum,schema=schema,table=table)
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except Exception as e :
            result = (" read DB err",e)
        
        return result

    def updateDB(self,schema,table,colum,value,condition):
        sql = " UPDATE {schema}.{table} SET {colum}='{value}' WHERE {colum}='{condition}' ".format(schema=schema
        , table=table , colum=colum ,value=value,condition=condition )
        try :
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e :
            print(" update DB err",e)

    def deleteDB(self,schema,table,condition):
        sql = " delete from {schema}.{table} where {condition} ; ".format(schema=schema,table=table,
        condition=condition)
        try :
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print( "delete DB err", e)

    def dropTable(self, schema, table):
        sql = "DROP TABLE IF EXISTS {schema}.{table};".format(schema=schema, table=table)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print("Drop table error", e)
            
if __name__ == "__main__":
    db = CRUD()
    # db.createTable(schema='myschema',table='table', columns=[('ID','text')])
    # db.insertDB(schema='myschema',table='table',colum='ID',data='유동적변경후')
    print(db.readDB(schema='public',table='sound',colum='*'))
    # db.updateDB(schema='myschema',table='table',colum='ID', value='와우',condition='유동적변경')
    # db.deleteDB(schema='myschema',table='table',condition ="id != 'd'")
    # db.dropTable('myschema', 'table')