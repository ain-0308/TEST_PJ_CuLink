import json
import gzip
import base64
from datetime import datetime
from db.settings import *
# 사용할 함수 불러오기
from utils.mysql_querys import query_metadata_from_db
from models.report_openai import createReport_openAI
from utils.firebase_utils import fetch_article_content
from models.textToImage import generate_images_and_send
from db.db_config import get_db_connection
from db.firebase_config import bucket

# datetime 변환 함수
def convert_datetime_in_metadata(metadata):
    for item in metadata:
        if isinstance(item.get('cr_art_date'), datetime):
            item['cr_art_date'] = item['cr_art_date'].isoformat()  # datetime을 문자열로 변환
    return metadata

def encode_images(report_images):
    encoded_images = []
    for image in report_images:
        try:
            encoded_image = {
                "file_name" : image["file_name"],
                "style" : image["style"],
                "image_data" : base64.b64encode(image["image_data"]).decode('utf-8')
            }
            encoded_images.append(encoded_image)
        except  KeyError as e:
            print(f"이미지 인코딩 키에러 {e}")
    return encoded_images

def createReport_services(id_list: list):
        try:
            connection = get_db_connection(database_config)
            # mySQL 데이터 조회 함수
            metadata = query_metadata_from_db(id_list, connection)
            # datetime을 문자열로 변환
            conv_metadata = convert_datetime_in_metadata(metadata)
            # Firebase 원문 조회
            article_contents = fetch_article_content(id_list,bucket)
            # 레포트 생성 모델 결과 값
            report_data = createReport_openAI(article_contents)
            # print("report_data", report_data)
            # 임의 문장 넣어보기
            text = report_data["img_txt"]
            # 생성된 이미지 바이너리 데이터
            report_images = generate_images_and_send(text)
            en_report_images = encode_images(report_images)
            # 바이너리 처리를 위해 딕셔너리로 묶어 주기
            combined_data = {
                'metadata' : conv_metadata,
                'report_titles':report_data['titles'],
                'report_data' : report_data["reports"],
                'report_images' : en_report_images,
                'created_at': datetime.now().isoformat(),
            }
            # JSON으로 직렬화
            json_text = json.dumps(combined_data).encode('utf-8')
            comprs_data = gzip.compress(json_text)
        except Exception as e:
            print("combined_data 압축 에러:", e)
        
        return comprs_data