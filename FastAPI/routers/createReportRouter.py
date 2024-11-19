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
    


""" 리액트쪽 레포트생성하기 요청후 데이터 받았을 때 예시 코드
import axios from 'axios';
import pako from 'pako';

async function fetchCompressedData() {
    try {
        const response = await axios.post("http://localhost:8000/report/createReport", {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids: 선택된 id리스트 }), // 선택된 기사를 JSON 형태로 전송
        });                         👆🏻 이 부분 ids로 보내주세요~

        const compressedData = await response.arrayBuffer();
        // 압축 해제
        const decompressedData = pako.inflate(new Uint8Array(compressedData));
        // UTF-8로 디코딩
        const textDecoder = new TextDecoder('utf-8');
        const jsonString = textDecoder.decode(decompressedData);
        // JSON 파싱
        const parsedData = JSON.parse(jsonString);
        console.log(parsedData);
        // 로그 보시면 object타입으로 넘어옵니다~
        // 거기서 필요한 것 가져다 쓰셔야해요~

    } catch (error) {
        console.error("Error fetching compressed data:", error);
    }
}
"""