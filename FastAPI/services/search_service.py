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
def search_by_fireindex(user_keywords):
    # 각 조건의 결과를 저장할 집합 초기화
    and_results = set()
    or_results = set()
    not_results = set()
    # Firestore에서 검색
    # 1. "and" 조건: 모든 필수 키워드가 포함된 기사만 남김
    for keyword in user_keywords.get('andKeywords',[]):
        doc_ref = fire_db.collection("keyword_index").document(keyword)
        doc = doc_ref.get()
        if doc.exists:
            article_ids = set(doc.to_dict().get("article_ids", []))
            if not and_results:
                and_results = article_ids  # 첫 번째 키워드는 전체 집합으로 초기화
            else:
                and_results.intersection_update(article_ids)  # 교집합으로 필터링
# 2. "or" 조건: 선택 키워드가 포함된 기사들을 모두 추가
    for keyword in user_keywords.get("orKeywords", []):
        doc_ref = fire_db.collection("keyword_index").document(keyword)
        doc = doc_ref.get()
        if doc.exists:
            article_ids = set(doc.to_dict().get("article_ids", []))
            or_results.update(article_ids)  # 합집합으로 추가

    # 3. "not" 조건: 제외 키워드가 포함된 기사들을 제외
    for keyword in user_keywords.get("notKeywords", []):
        doc_ref = fire_db.collection("keyword_index").document(keyword)
        doc = doc_ref.get()
        if doc.exists:
            article_ids = set(doc.to_dict().get("article_ids", []))
            not_results.update(article_ids)  # 제외할 기사 IDs 추가

# 최종 결과: "and" 조건에 맞는 기사 중에서 "not" 조건을 제외하고 "or" 조건과 결합
    final_results = (and_results - not_results)  # "and" 결과에서 "not"을 제외
    if or_results:
        final_results.update(or_results)  # "or" 조건을 포함한 기사 추가
    print('final_results',final_results)
    return final_results

def default_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} is not serializable")

# ============== 검색 함수 ==================
def search_by_keyword_and_date(user_keywords, date_list):
    connection = get_db_connection(database_config)
    article_contents = []
    article_metadata = []

    if not user_keywords and date_list:
        id_list = []
        article_metadata = all_query(id_list, date_list, connection)
        id_list = [record['cr_art_id'] for record in article_metadata]
        article_contents = fetch_article_content(id_list,bucket)

    elif user_keywords and date_list or not date_list :
        # 키워드가 있을 때 (날짜가 있는 경우와 없는 경우를 포함)
        id_list = search_by_fireindex(user_keywords)
        article_metadata = all_query(id_list, date_list, connection)
        id_list_m = [record['cr_art_id'] for record in article_metadata]
        article_contents = fetch_article_content(id_list_m,bucket)

    articles_data = {
        "metadata": article_metadata,
        "contents": article_contents
    }
    json_text = json.dumps(articles_data, default=default_serializer).encode('utf-8')
    articles_data_gzip = gzip.compress(json_text)
    return articles_data_gzip
