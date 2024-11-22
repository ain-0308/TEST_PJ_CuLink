# 필요한 모듈 임포트
from huggingface_hub import login
from datetime import datetime
import requests
from PIL import Image
from deep_translator import GoogleTranslator
from db.settings import huggingface_token

# Hugging Face 로그인
try:
    login(token=huggingface_token, add_to_git_credential=True)
    print("로그인 성공!!")
except Exception as e:
    print(f"로그인 실패: {e}")

# Hugging Face API 설정
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": f"Bearer {huggingface_token}"}

# ================== 한글 키워드 번역 파트 ======================
# 한글 => 영어 번역함수
def translate_kr_to_en(keyword_ko):
    # 번역기 설정
    translator = GoogleTranslator(source='en', target='ko')
    # 번역 수행
    keyword_en = translator.translate(keyword_ko)
    # 번역 결과 출력
    return keyword_en

def query(payload):
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        print("API 응답 상태코드: ", response.status_code)
        if response.status_code == 200:
            print("API 요청 성공!")
            return response.content  # 이미지 데이터
        else:
            print(f"API 요청 실패: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"API 요청 중 에러 발생: {e}")
        return None

#=================== 이미지 3가지 버전 생성 ======================
def generate_images(keyword, styles):
    images = []
    for style in styles:
        retry_count = 0
        max_retries = 5  # 재시도 횟수 설정
        while retry_count < max_retries:
            # 이미지 생성 시도
            prompt = f"{keyword} in {style} style"
            image_bytes = query({"inputs": prompt})
            # 이미지가 유효한지 확인하는 부분 추가
            if image_bytes:
                images.append((style, image_bytes))
                break
            else:
                print(f"이미지 생성 실패 스타일 : {style}")
                retry_count += 1
        if retry_count == max_retries: # 재시도 후에도 실패시
            print(f"생성 시도한 {style} 스타일 {max_retries}회 시도 후 실패 ")
    return images

#================ 이미지를 생성하고 FastAPI로 전송하는 함수 ==============
def generate_images_and_send(translated_text):
    print("이미지 생성 함수 시작")
    styles = ["watercolor", "comic", "photorealistic"]  # 스타일 리스트

    # 번역된 키워드를 키워드 변수에 할당
    keyword = translate_kr_to_en(translated_text)
    print(f"번역된 키워드: {keyword}")

    # 이미지 생성 결과 할당
    image_versions = generate_images(keyword, styles)
    
    # 생성된 이미지를 리스트에 딕셔너리 형태로 변환
    images = []
    for style, image_bytes in image_versions:
        try:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # 현재시간
            file_name = f"{timestamp}-image_{style}.jpg"  # 파일명 구성
            
            # 이미지 데이터를 추가
            images.append({
                "file_name": file_name,
                "style": style,
                "image_data": image_bytes
            })
        except Exception as e:
            print(f"이미지 구성 중 에러 발생 ({style}): {e}")
    print("이미지 생성 완료")
    return images