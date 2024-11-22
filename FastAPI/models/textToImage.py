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
    translator = GoogleTranslator(source='ko', target='en')
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
    # 스타일별 프롬프트 정의
    # 스타일별 프롬프트 정의
    prompts = {
        "watercolor": "Create an image of {summary}, depicted as a beautiful watercolor painting. The artwork should feature flowing, soft hues and delicate brushstrokes that evoke a sense of harmony. If people are present, portray them with soft, natural details, realistic facial features, and body proportions. Incorporate natural elements like light diffusion and smooth blending of colors for a tranquil and serene atmosphere. Text, if included, should be legible and seamlessly integrated into the composition.",
        "comic": "Generate an image of {summary} illustrated in a bold and dynamic comic book style. The scene should include sharp outlines, high-contrast vivid colors, and a sense of movement. If people are present, ensure their poses are dynamic, with exaggerated yet accurate expressions and body proportions. Integrate bold text seamlessly into the design, using stylized word bubbles or captions to enhance the comic aesthetic. Ensure an energetic and visually striking composition.",
        "photorealistic": "Render {summary} as a highly detailed photorealistic image. Emphasize natural textures, lifelike proportions, and realistic lighting effects, such as accurate shadows, reflections, and atmospheric details. If people are present, depict them with precise facial features, natural expressions, and proportional bodies. Ensure all elements, including any text, are sharp and realistically embedded into the environment to create an immersive experience."
    }

    images = []  # 생성된 이미지를 저장할 리스트
    for style in styles:
        retry_count = 0
        max_retries = 6  # 재시도 횟수 설정
        while retry_count < max_retries:
            # 스타일별 프롬프트와 요약된 번역 문장 조합
            prompt = prompts.get(style, "{summary}").format(summary=keyword)
            print(f"{style} 스타일 이미지 생성 프롬프트: {prompt}")

            # 이미지 생성 시도
            image_bytes = query({"inputs": prompt})
            
            # 이미지가 유효한지 확인
            if image_bytes:
                print(f"{style} 스타일 이미지 생성 성공!")
                images.append((style, image_bytes))
                break
            else:
                print(f"이미지 생성 실패 스타일: {style}")
                retry_count += 1
        
        # 최대 재시도 횟수 도달 시 실패 로그 출력
        if retry_count == max_retries:
            print(f"생성 시도한 {style} 스타일 {max_retries}회 시도 후 실패")
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