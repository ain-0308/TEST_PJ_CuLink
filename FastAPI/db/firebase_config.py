import firebase_admin
from firebase_admin import credentials, storage, firestore
from db.settings import firebase_key
# 이미 초기화된 경우 에러 방지
if not firebase_admin._apps:
    # Firebase 초기화
    cred = credentials.Certificate(firebase_key)
    firebase_admin.initialize_app(cred, {'storageBucket': 'news-data01.appspot.com'})

# 버킷 할당
bucket = storage.bucket()

fire_db = firestore.client()