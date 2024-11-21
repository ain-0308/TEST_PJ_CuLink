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
    
