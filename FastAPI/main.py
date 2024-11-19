# main.py의 맨 위쪽에 추가
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 요약하기 라우터
from routers.summarizationRouter import router as summarization_router
# 레포트 생성 라우터
from routers.createReportRouter import router as createReport_router
# 검색 라우터
from routers.searchRouter import router as searchRouter
# 뉴스데이터 라우터
from routers.articlesRouter import router as articles_router
# 레포트 저장 라우터 
from routers.saveReportRouter import router as saveReport_router
# 챗봇 라우터
from routers.chatbotRouter import router as chatbot_router
# 라우터 초기화
app = FastAPI()

# CORS 설정: React 앱에서 오는 요청 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요약모델 라우터 
app.include_router(summarization_router, prefix="/summarize") 
# 레포트 생성 라우터
app.include_router(createReport_router, prefix="/report") 
# 검색 라우터 
app.include_router(searchRouter, prefix="/search") 
# articles 라우터 등록 
app.include_router(articles_router) 
# 레포트 저장 라우터
app.include_router(saveReport_router)
# 챗봇 라우터
app.include_router(chatbot_router)

@app.get("/") # fastapi주소로 진입시 
async def root():
    return {"message": "Hello, FastAPI!"}