import boto3
import firebase_admin
from firebase_admin import credentials, storage, firestore
import json
import logging
# AWS Secrets Manager 클라이언트 생성
def get_firebase_key():
    client = boto3.client("secretsmanager", region_name="ap-northeast-2")
    try:
        print("Fetching Firebase Key from Secrets Manager...")
        response = client.get_secret_value(SecretId="FIREBASE_KEY")
        firebase_key = json.loads(response["SecretString"])
        return firebase_key
    except Exception as e:
        print(f"Error fetching Firebase Key: {e}")
        raise

# Firebase 초기화
def initialize_firebase():
    try:
        firebase_key = get_firebase_key()
        logging.info("Successfully fetched Firebase Key.")
        # Firebase 인증 설정
        cred = credentials.Certificate(firebase_key)
        if not firebase_admin._apps:  # Firebase 중복 초기화 방지
            firebase_admin.initialize_app(cred, {"storageBucket": "news-data01.appspot.com"})

        # 버킷 및 Firestore 클라이언트 초기화
        bucket = storage.bucket()
        fire_db = firestore.client()
        logging.info("Firebase storage and Firestore initialized.")
        return bucket, fire_db
    
    except Exception as e:
        logging.error(f"Error initializing Firebase: {e}")
        raise
try:
    bucket, fire_db = initialize_firebase()
    print("Firebase initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase: {e}")