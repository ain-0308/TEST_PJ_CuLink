import firebase_admin
from firebase_admin import credentials, storage, firestore
import boto3
import json
# Secrets Manager 클라이언트 생성
client = boto3.client("secretsmanager", region_name="ap-northeast-2")
try:
    print("Fetching Firebase Key...")
    # 비밀 값 가져오기
    response = client.get_secret_value(SecretId="FIREBASE_KEY")
    print("Response:", response)
    firebase_key = json.loads(response["SecretString"])
    # Firebase 초기화
    cred = credentials.Certificate(firebase_key)
    firebase_admin.initialize_app(cred, {'storageBucket': 'news-data01.appspot.com'})

    # 버킷 할당
    bucket = storage.bucket()

    fire_db = firestore.client()
except Exception as e:
    print(f"파이어베이스쪽 에러남 키를 못 가져온건가..{e}")