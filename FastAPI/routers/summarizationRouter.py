from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from models.summary_openai import summarize_article  # 요약 함수 임포트
from utils.firebase_utils import fetch_article_content

from firebase_admin import storage  # Firebase 스토리지 사용

router = APIRouter()

# 여러 기사 ID와 제목을 받기 위한 데이터 모델 정의
class Article(BaseModel):
    cr_art_id: int
    cr_art_title: str
    cr_art_url : str

class Articles(BaseModel):
    articles: List[Article]

# 요약하기 엔드포인트
@router.post("/summarize-article")
async def receive_article_contents(articles: Articles):
    try:
        # 받은 기사 내용들을 추출
        article_ids = [article.cr_art_id for article in articles.articles]
        article_titles = {article.cr_art_id: article.cr_art_title for article in articles.articles}
        article_url = {article.cr_art_id: article.cr_art_url for article in articles.articles}
        print(f"받은 기사 ID들: {article_ids}")

        # Firebase에서 기사 원문을 가져오기
        bucket = storage.bucket()  # Firebase 버킷 객체 생성
        contents = fetch_article_content(article_ids, bucket)
        print(f"가져온 기사 원문: {contents}")

        # 각 기사 내용에 대해 요약 수행
        summarized_contents = []
        for content_dict in contents:
            for article_id, content in content_dict.items():
                # 요약 함수 호출
                summary = summarize_article(content)
                # ID, 제목, 요약 내용을 포함한 결과 추가
                summarized_contents.append({
                    "cr_art_id": article_id,
                    "cr_art_title": article_titles[article_id],
                    "cr_art_url":article_url[article_id],
                    "summary": summary
                })

        # 요약된 결과를 반환
        return JSONResponse(content={"summarized_contents": summarized_contents, "message": "기사 내용이 성공적으로 요약되었습니다."})

    except Exception as e:
        print(f"Error during content summarization: {str(e)}")
        raise HTTPException(status_code=400, detail=f"기사 요약 처리 중 오류 발생: {str(e)}")
