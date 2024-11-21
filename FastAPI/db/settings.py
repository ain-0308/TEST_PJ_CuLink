import os
from dotenv import load_dotenv
# 환경 변수 로드
load_dotenv()

import boto3
import json
import os

def get_secrets(secret_name, region_name='ap-northeast-2'):
    # Secrets Manager 클라이언트 생성
    client = boto3.client('secretsmanager', region_name=region_name)
    try:
        # 시크릿 값 가져오기
        response = client.get_secret_value(SecretId=secret_name)
        secret = response['SecretString']
        return json.loads(secret)
    except Exception as e:
        print(f"Error retrieving secrets: {e}")
        return None

# 시크릿에서 환경 변수 가져오기
secrets = get_secrets("env_key")
if secrets:
    for key, value in secrets.items():
        os.environ[key] = value
        print(f"Set environment variable for {key}")
    

#================= mySQL ========================
database_config = {
    "DB_PORT" : int(os.getenv("DB_PORT")),
    "DB_HOST" : os.getenv("DB_HOST"),
    "DB_USER" : os.getenv("DB_USER"),
    "DB_PASSWORD" : os.getenv("DB_PASSWORD"),
    "DB_DATABASE" : os.getenv("DB_DATABASE"),}

#================== openAI_key ==================
openai_key = secrets["OPEN_API_KEY"]

#================= HUGGINGFACE ==================
huggingface_token = secrets["HUGGINGFACE_TOKEN"]

#================= 벡터 모델 경로 ================
model_dir = secrets['VECTOR_MODEL_DIR']