# 4. Firebase 관련 라이브러리
import firebase_admin
from firebase_admin import credentials, storage
import json
import boto3

# Secrets Manager 클라이언트 생성
client = boto3.client("secretsmanager", region_name="ap-northeast-2")

# 비밀 값 가져오기
response = client.get_secret_value(SecretId="FIREBASE_KEY")
firebase_key = json.loads(response["SecretString"])

# Firebase 초기화
cred = credentials.Certificate(firebase_key)
firebase_admin.initialize_app(cred, {'storageBucket': 'news-data01.appspot.com'})

# Firebase에서 기사 원문 가져오기 함수
def fetch_article_content(article_ids):
    """Firebase 스토리지에서 기사 원문 가져오기"""
    # 가져온 content를 담을 리스트
    contents = []
    # id값과 content를 넣을 딕셔러니 초기화
    content = {}
    try:
        for article_id in article_ids:
            article_id = int(article_id)
            # 버킷 접근
            bucket = storage.bucket()
            blob = bucket.blob(f"articles/{article_id}.json")

            # JSON 파싱
            raw_content = blob.download_as_text()
            parsed_content = json.loads(raw_content)
            # content 가져오기
            content = {article_id : parsed_content.get("content", "Content not available.")}
            # 딕셔너리형태의 content 리스트에 넣기
            contents.append(content)
            

    except json.JSONDecodeError as e:
        print(f"JSON으로 바꾸다 에러남 그 id는 => {article_id}: {str(e)}")
        contents[article_id] = "Invalid content format."
        
    except Exception as e:
        print(f"Storage 조회 오류  {article_id}: {str(e)}")
        return "Content not available."
    # 반환
    return contents
