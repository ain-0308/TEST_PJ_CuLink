from fastapi import HTTPException
import pymysql
from pymysql.cursors import DictCursor
from db.settings import database_config
# 포트번호는 정수로 받아야 함

# MySQL 연결 설정
def get_db_connection(database_config):
    try:    
        return pymysql.connect(
            host=database_config["DB_HOST"],
            user=database_config["DB_USER"],
            password=database_config["DB_PASSWORD"],
            database=database_config["DB_DATABASE"],
            port=database_config["DB_PORT"],
            cursorclass=DictCursor)
            # 결과를 딕셔너리 형태로 반환)
    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")  # 상세한 오류 로그
        raise HTTPException(status_code=500, detail="Database connection failed")
    except Exception as e:
        print(f"General Error: {e}")  # 기타 오류 로그
        raise HTTPException(status_code=500, detail="Internal Server Error")