import json

# Firebase에서 기사 원문 가져오기 함수
def fetch_article_content(article_ids,bucket):
    """Firebase 스토리지에서 기사 원문 가져오기"""
    # 가져온 content를 담을 리스트
    contents = []
    # id값과 content를 넣을 딕셔러니 초기화
    content = {}
    try:
        for article_id in article_ids:
            article_id = int(article_id)
            # 버킷 접근
            
            blob = bucket.blob(f"articles/{article_id}.json")

            # JSON 파싱
            raw_content = blob.download_as_text()
            parsed_content = json.loads(raw_content)
            # content 가져오기
            content = {article_id : parsed_content.get("content", "Content not available.")}
            # 딕셔너리형태의 content 리스트에 넣기
            contents.append(content)
            

    except json.JSONDecodeError as e:
        print(f"JSON decoding error for article {article_id}: {str(e)}")
        contents[article_id] = "Invalid content format."
        
    except Exception as e:
        print(f"Storage 조회 오류  {article_id}: {str(e)}")
        return "Content not available."
    # 반환
    # print('조회된 파이어베이스 원문',contents[1])
    return contents
