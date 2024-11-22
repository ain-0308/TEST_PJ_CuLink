import json
import gzip
from db.settings import *
from datetime import datetime
# 프로젝트 내부 모듈
from utils.mysql_querys import all_query
from utils.firebase_utils import fetch_article_content
from db.db_config import get_db_connection
from db.firebase_config import bucket, fire_db

# ================ firebase에서 키워드 검색 함수 =======================
def search_by_fireindex(user_keywords: dict):
    # 각 조건의 결과를 저장할 집합 초기화
    print('user_keywords',user_keywords)
    and_results = set()
    or_results = set()
    not_results = set()
    final_results = set()
    # Firestore에서 검색
    # "and" 조건: 필수 키워드가 포함된 기사들의 교집합
    and_keywords = user_keywords.get('andKeywords', [])
    print('and_keywords',and_keywords)
    if and_keywords:  # 리스트가 비어 있지 않을 때만 실행
        for keyword in and_keywords:
            doc_ref = fire_db.collection("keyword_index").document(keyword)
            doc = doc_ref.get()
            if doc.exists:
                article_ids = set(doc.to_dict().get("article_ids", []))
                if not and_results:
                    and_results = article_ids  # 첫 번째 키워드는 전체 집합으로 초기화
                else:
                    and_results.intersection_update(article_ids)  # 교집합으로 필터링

    # "or" 조건: 선택 키워드가 포함된 기사들을 모두 추가
    or_keywords = user_keywords.get("orKeywords", [])
    print('or_keywords',or_keywords)
    if or_keywords:  # 리스트가 비어 있지 않을 때만 실행
        for keyword in or_keywords:
            print('or_keywords의 keyword',keyword)
            doc_ref = fire_db.collection("keyword_index").document(keyword)
            doc = doc_ref.get()
            print('doc',doc)
            if doc.exists:
                article_ids = set(doc.to_dict().get("article_ids", []))
                or_results.update(article_ids)  # 합집합으로 추가

    # "not" 조건: 제외 키워드가 포함된 기사들을 제외
    not_keywords = user_keywords.get("notKeywords", [])
    print('not_keywords',not_keywords)
    if not_keywords:  # 리스트가 비어 있지 않을 때만 실행
        for keyword in not_keywords:
            doc_ref = fire_db.collection("keyword_index").document(keyword)
            doc = doc_ref.get()
            if doc.exists:
                doc_data = doc.to_dict() or {}  # None인 경우 빈 딕셔너리로 처리
                article_ids = set(doc_data.to_dict().get("article_ids", []))
                not_results.update(article_ids)  # 제외할 기사 IDs 추가

# 최종 결과 계산
    final_results = (and_results - not_results)  # "and" 조건에서 "not" 조건 제외
    if or_results:
        final_results.update(or_results)  # "or" 조건 추가

    print('final_results before check:', final_results)
    if not final_results:  # 결과가 비어있으면 빈 집합으로 처리
        return None

    print('final_results:', final_results)
    return final_results


def default_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} is not serializable")

# ============== 검색 함수 ==================
def search_by_keyword_and_date(user_keywords: dict, date_list: list = None):
    connection = get_db_connection(database_config)
    article_metadata = []

    # Firebase에서 기사 본문 가져오기 함수를 검색 함수 내부에 정의
    def fetch_article_content(article_ids, bucket):
        """Firebase 스토리지에서 기사 원문 가져오기"""
        contents = []
        try:
            for article_id in article_ids:
                article_id = int(article_id)
                # Firebase 버킷 접근
                blob = bucket.blob(f"articles/{article_id}.json")

                # JSON 파싱
                raw_content = blob.download_as_text()
                parsed_content = json.loads(raw_content)
                # 기사 본문만 추가
                content = parsed_content.get("content", "Content not available.")
                contents.append(content)

        except json.JSONDecodeError as e:
            print(f"JSON decoding error for article {article_id}: {str(e)}")
            contents.append("Invalid content format.")
            
        except Exception as e:
            print(f"Storage 조회 오류 {article_id}: {str(e)}")
            contents.append("Content not available.")
            
        return contents

    if not user_keywords and date_list:
        id_list = []
        article_metadata = all_query(id_list, date_list, connection)
        id_list = [str(record['cr_art_id']) for record in article_metadata]  # ID를 문자열로 변환
        contents = fetch_article_content(id_list, bucket)

        # metadata에 기사 본문 병합
        for idx, metadata in enumerate(article_metadata):
            metadata['cr_art_id'] = str(metadata['cr_art_id'])  # ID를 문자열로 변환
            metadata['cr_art_content'] = contents[idx] if idx < len(contents) else None

    elif user_keywords and date_list or not date_list:
        # 키워드가 있을 때 (날짜가 있는 경우와 없는 경우를 포함)
        id_list = search_by_fireindex(user_keywords)
        if not id_list:  # 검색 결과가 없는 경우
            return {"message": "검색된 기사가 없습니다."}
        article_metadata = all_query(id_list, date_list, connection)
        id_list_m = [str(record['cr_art_id']) for record in article_metadata]  # ID를 문자열로 변환
        contents = fetch_article_content(id_list_m, bucket)

        # metadata에 기사 본문 병합
        for idx, metadata in enumerate(article_metadata):
            metadata['cr_art_id'] = str(metadata['cr_art_id'])  # ID를 문자열로 변환
            metadata['cr_art_content'] = contents[idx] if idx < len(contents) else None

    # 결과가 없으면 메시지 반환
    if not article_metadata:
        return {"message": "검색된 기사가 없습니다."}

    # JSON 직렬화 후 압축
    json_text = json.dumps(article_metadata, default=default_serializer).encode('utf-8')
    articles_data_gzip = gzip.compress(json_text)
    return articles_data_gzip
