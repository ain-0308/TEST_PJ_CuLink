from fastapi import APIRouter
from pydantic import BaseModel
from models.chatbot_openai import get_chatbot_response

router = APIRouter()

# 요청 데이터 모델 정의
class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat_endpoint(request: ChatRequest):
    user_message = request.message
    print(f"요청 메시지: {user_message}")  # 요청 로그
    response = get_chatbot_response(user_message)
    print(f"응답 메시지: {response}")  # 응답 로그
    return {"reply": response}  # 올바른 응답 반환
