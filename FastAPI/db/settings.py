import os
from dotenv import load_dotenv
# 환경 변수 로드
load_dotenv()
#================= mySQL ========================
database_config = {
    "DB_PORT" : int(os.getenv("DB_PORT")),
    "DB_HOST" : os.getenv("DB_HOST"),
    "DB_USER" : os.getenv("DB_USER"),
    "DB_PASSWORD" : os.getenv("DB_PASSWORD"),
    "DB_DATABASE" : os.getenv("DB_DATABASE"),}

#================== FAISS =======================
faiss_path = os.getenv('FAISS_INDEX_PATH')

#================== Firebase ====================
firebase_key = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')

#================== openAI_key ==================
openai_key = os.getenv("OPEN_API_KEY")
summary_openai_key = os.getenv("SUMMARY_OPEN_API_KEY")
report_openai_key = os.getenv("REPORT_OPEN_API_KEY")
chatbot_openai_key = os.getenv("CHATBOT_OPEN_API_KEY")

#================= HUGGINGFACE ==================
huggingface_token = os.getenv("HUGGINGFACE_TOKEN")

#================= 벡터 모델 경로 ================
model_dir = os.getenv('VECTOR_MODEL_DIR')