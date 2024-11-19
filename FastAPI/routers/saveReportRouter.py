from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Union, Any
from db.firebase_config import bucket  # Firebase bucket import
from db.db_config import get_db_connection, database_config  # Database connection import
import base64
import uuid
from datetime import datetime

router = APIRouter()

# 보고서 데이터 모델 정의
class ReportData(BaseModel):
    user_id: str
    title: str
    image: str  # Base64 인코딩된 이미지
    content: str
    art_ids: Optional[List[Union[int, str, Any]]] = []  # 선택한 기사 ID 리스트 (int 또는 str 가능)

# Firebase에 이미지를 업로드하고 URL 반환 함수
def upload_image_to_firebase(image_data: str, rep_id: int):
    # 파일 이름을 rep_id로 설정하여 Firebase images 폴더에 저장
    file_name = f"images/{rep_id}.png"
    blob = bucket.blob(file_name)

    # Base64 이미지 데이터를 디코드하여 Firebase에 업로드
    image_bytes = base64.b64decode(image_data.split(",")[1])  # "data:image/png;base64," 제거 후 디코딩
    blob.upload_from_string(image_bytes, content_type="image/png")

    # 업로드된 이미지의 URL 생성
    image_url = f"https://storage.googleapis.com/{bucket.name}/{file_name}"
    return image_url

# 보고서 저장 엔드포인트
@router.post("/savereport")
async def save_report(report_data: ReportData):
    try:
        # 63비트 숫자형 UUID 생성
        rep_id = uuid.uuid4().int & ((1 << 63) - 1)

        # Firebase에 이미지 업로드 및 URL 가져오기
        image_url = upload_image_to_firebase(report_data.image, rep_id)

        # MySQL에 보고서 데이터 저장 (이미지 URL 제외)
        db_connection = get_db_connection(database_config)
        cursor = db_connection.cursor()

        # 현재 날짜와 시간을 rep_date에 저장
        rep_date = datetime.now()

        # Reports 테이블에 보고서 데이터 삽입
        sql = """
            INSERT INTO Reports (rep_id, rep_title, rep_content, rep_date, user_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (rep_id, report_data.title, report_data.content, rep_date, report_data.user_id)
        cursor.execute(sql, values)

        # ArticleReports 테이블에 art_id와 rep_id 연결 데이터 삽입
        if report_data.art_ids:
            article_reports_sql = "INSERT INTO ArticleReports (rep_id, art_id) VALUES (%s, %s)"
            # art_ids의 각 항목을 int로 변환하여 저장
            article_reports_values = [(rep_id, int(art_id)) for art_id in report_data.art_ids if isinstance(art_id, (int, str))]
            cursor.executemany(article_reports_sql, article_reports_values)

        # 변경 사항을 커밋
        db_connection.commit()
        
        # 연결 닫기
        cursor.close()
        db_connection.close()

        return {"message": "Report saved successfully", "rep_id": rep_id, "image_url": image_url}
    except Exception as e:
        print(f"Error saving report: {e}")
        raise HTTPException(status_code=500, detail="Failed to save report")
