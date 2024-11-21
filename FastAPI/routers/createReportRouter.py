from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import List,Optional,Any, Union
# 서비스 폴더의 레포트 생성 함수
from services.report_service import createReport_services

# 라우터 초기화
router = APIRouter()

# 리액트로부터 전달 받은 id 타입 정의
class ArticleIdList(BaseModel):
    ids: Optional[List[Union[int, str, Any]]] = []

@router.post('/createReport')
def createReport(request: ArticleIdList):
    try:
        # ids가 리스트인지 확인하고, 아니라면 오류 반환
        if not isinstance(request.ids, list):
            raise HTTPException(status_code=400, detail="ids 필드는 리스트 형식이어야 합니다.")
        print("Received IDs:", request.ids)

        print("레포트 생성 시작")
        comprs_data = createReport_services(request.ids)
        print(comprs_data)
        
        # 리액트로 전달할 값
        print("레포트 전송 완료")
        return Response(content=comprs_data,  media_type="application/octet-stream")
    
    except Exception as e:
        print(f"Error during ID reception: {str(e)}")
        raise HTTPException(status_code=400, detail=f"기사 ID 처리 중 오류 발생: {str(e)}")
    