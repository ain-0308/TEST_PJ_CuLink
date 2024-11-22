import re
import openai
from db.settings import openai_key

# API 키 설정
openai.api_key = openai_key  # OpenAI API 키

def create_report_openai(article_contents):
    """
    3가지 유형의 보고서를 생성하여 반환합니다.
    """
    try:
        # 프롬프트 목록 정의
        prompt_templates = [
            {
                "name": "summary",
                "prompt": """
                당신은 뛰어난 보고서 작성자입니다.
                
                아래 기사 내용을 읽고 요약 보고서를 작성하세요:
                1. 제목은 첫 번째 줄에 작성하며, 15단어 또는 50자 이내로 제한합니다.
                2. 본문은 서론, 본론, 결론 구조로 간결하게 작성하고, 핵심 내용만 포함하세요.
                3. 보고서는 한국어로 작성하세요.

                기사 내용:
                {article_contents}

                결과:
                """
            },
            {
                "name": "analysis",
                "prompt": """
                당신은 심층 분석을 전문으로 하는 보고서 작성자입니다.
                
                아래 기사 내용을 분석하여 보고서를 작성하세요:
                1. 제목은 첫 번째 줄에 작성하며, 15단어 또는 50자 이내로 제한합니다.
                2. 본문은 서론, 본론, 결론으로 구성하며, 구체적인 수치, 사례, 데이터 분석을 포함하세요.
                3. 논리적으로 구성된 분석 내용을 기반으로 작성하고, 중요한 통찰력을 제공합니다.
                4. 보고서는 한국어로 작성하세요.

                기사 내용:
                {article_contents}

                결과:
                """
            },
            {
                "name": "solution",
                "prompt": """
                당신은 문제 해결과 제안을 전문으로 하는 보고서 작성자입니다.
                
                아래 기사 내용을 읽고, 문제를 식별하고 이에 대한 실질적인 해결책과 제안을 포함하는 보고서를 작성하세요:
                1. 제목은 첫 번째 줄에 작성하며, 15단어 또는 50자 이내로 제한합니다.
                2. 본문은 서론, 본론, 결론으로 구성하며, 문제 상황, 원인 분석, 해결책 제안, 실행 가능한 아이디어를 포함하세요.
                3. 보고서는 한국어로 작성하세요.

                기사 내용:
                {article_contents}

                결과:
                """
            }
        ]

        # 결과 저장 리스트
        reports = []

        for template in prompt_templates:
            prompt = template["prompt"].format(article_contents=article_contents)
            
            # OpenAI 호출
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional report writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.7,
            )
            
            # 응답 처리
            response_content = response['choices'][0]['message']['content'].strip()
            title, body = parse_response(response_content)
            
            # 보고서 저장
            reports.append({
                "type": template["name"],
                "title": title,
                "body": body
            })

        return reports

    except Exception as e:
        print(f"Error generating reports: {e}")
        return {"error": str(e)}

def parse_response(response_content):
    """
    GPT 응답에서 제목과 본문을 분리합니다.
    """
    # 제목과 본문 분리
    title_match = re.match(r"^(.*?)(?:\n|\r\n)(.*)", response_content, re.S)
    if not title_match:
        raise ValueError("응답에서 제목과 본문을 분리할 수 없습니다.")
    
    title = title_match.group(1).strip()
    body = title_match.group(2).strip()
    
    # 제목 길이 확인 및 수정
    if len(title) > 50:
        title = title[:50] + "..."  # 길이를 초과한 제목은 자름

    return title, body

def create_report_text(report_contents):
    """
    보고서 본문 내용을 바탕으로 이미지 생성 문장을 작성합니다.
    """
    try:
        # 프롬프트 정의
        prompt = f"""
        당신은 시각적 이미지를 설명하는 전문 작가입니다.
        아래 보고서를 읽고, 이미지로 표현할 수 있는 문장을 작성하세요:
        
        1. 이미지화 가능한 시각적 요소를 포함합니다 (예: 사람, 장소, 물체 등).
        2. 완전한 문장으로 작성하며, 내용의 핵심을 정확히 표현합니다.
        3. 한국어로 작성하세요.

        보고서 내용:
        {report_contents}

        이미지 생성 문장:
        """
        
        # OpenAI 호출
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a skilled visual descriptor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=90,
            temperature=0.5,
        )

        # 응답 처리
        response_content = response['choices'][0]['message']['content'].strip()
        if not response_content:
            raise ValueError("이미지 생성 문장을 생성하지 못했습니다.")
        
        return response_content
    
    except Exception as e:
        print(f"Error generating image text: {e}")
        return ""

# 보고서 생성 함수 테스트
def generate_reports_and_images(article_contents_list):
    """
    여러 기사 내용을 기반으로 보고서를 생성하고, 이미지 생성 문장을 작성합니다.
    """
    results = []
    
    for article_contents in article_contents_list:
        reports = create_report_openai(article_contents)
        if "error" in reports:
            results.append({"error": reports["error"]})
            continue
        
        # 각 보고서에 대해 이미지 생성 문장을 추가
        for report in reports:
            img_text = create_report_text(report["body"])
            report["img_text"] = img_text
        
        results.append(reports)
    
    return results
