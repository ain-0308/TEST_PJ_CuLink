# 임시 모델 파일
import os
from dotenv import load_dotenv
import openai
from langchain_community.llms import OpenAI
# 환경 변수 로드
load_dotenv()

openai_key = os.getenv("OPEN_API_KEY")

# API 키 설정
summary_openai_key = os.getenv("SUMMARY_OPEN_API_KEY")

# 뉴스 요약 함수 article_content : 넘겨준 기사 원문 데이터
def summarize_article(article_content: str) -> str:
    # 요약 프롬프트 설정
    prompt_text = f"""
    You're a talented news summarizer, and your role is to create concise summaries that accurately reflect the key takeaways and important details of each article.

    When summarizing articles, keep the following in mind

    1. limit the length of your summary to a minimum of 50 characters and a maximum of 250 characters, within a range of 10-30% of the length of the article.
    2. Write all sentences in complete form, concise, and flowing naturally.
    ** If you encounter an incomplete sentence, delete it. **
    3. Include only key information and omit unnecessary details. Be sure to include key information (e.g., announcement date, key people, organization name, key policy objectives) to ensure the summary is clear.
    4. Avoid redundant phrasing and consolidate sentences with overlapping meaning into one to keep it concise.
    5. Improve readability by adding line breaks at the end of each sentence. Line breaks are added using the `\\n` character.
    **Write your summary in Korean. **
    6. Always maintain a consistent tone of voice when writing summaries.

    Article:
    {article_content}

    Summary:
    """


    # OpenAI ChatCompletion API 호출
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for summarizing news articles."},
            {"role": "user", "content": prompt_text}
        ],
        max_tokens=300,
        temperature=0.4
    )

    # 모델로부터 받은 요약 결과를 정리하여 summary_result에 저장
    summary = response['choices'][0]['message']['content'].strip()
    sentences = [sentence.strip() for sentence in summary.split('.') if sentence]
    formatted_summary = '.\n'.join(sentences)

    # 마지막 문장에 마침표 추가
    if not formatted_summary.endswith('.'):
        formatted_summary += '.'

    # 결과를 summary_result 변수에 저장
    summary_result = formatted_summary

    # 결과 출력
    print('summary_result',summary_result)
    return summary_result