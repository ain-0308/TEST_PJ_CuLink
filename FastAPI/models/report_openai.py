import openai
from langchain_community.llms import OpenAI


def createReport_text(report_contents):
    report_content = report_contents[0]
        # 프롬프트 설정: 보고서에서 핵심 문장 생성 요청
    summary_prompt = f"""
    You're a skilled visual descriptor, and you're tasked with identifying key takeaways from a report and using them to generate specific sentences for image creation.

    Using the following report as a guide, write key sentences that can be visualized as an image. As you write, keep in mind that you should

    1. use specific and clear wording that is suitable for visualization in images.
    2. include visual elements (e.g., people, places, key objects, or iconic scenes) that can effectively represent the topic of the report so that the key messages of that topic can be visualized.
    3. Use language that reveals the main mood or setting of the report, and link to images that help readers understand the topic.
    4. Key points should be clearly expressed, ending in complete sentences.
    5. Please write key sentences in Korean.

    Report Content:
    {report_content}

    Key sentences for image generation : 
    """

    # OpenAI API 호출
    summary_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for analyzing and summarizing documents."},
            {"role": "user", "content": summary_prompt}
        ],
        max_tokens=90,
        temperature=0.5,
        request_timeout=10
    )

    # 응답 유효성 확인
    response_content = summary_response['choices'][0].get('message', {}).get('content', '').strip()
    if not response_content:
        raise ValueError("OpenAI 응답에서 유효한 내용을 찾을 수 없습니다.")
    return response_content


def createReport_openAI(article_contents):
    try:
        # 3개의 프롬프트 템플릿
        prompt_text_templates = [
            f"""
            You're a talented report writer.

            Your task is to create reports based on articles from multiple disciplines. These reports should highlight notable patterns, data, and insights in a professional and concise manner.

            When writing a report, follow these strict guidelines:
            1. **The first line of the report must be a concise title that accurately represents the content. The title must be no longer than 15 words or 50 characters.** If the title exceeds this limit, the entire report will be invalidated. Use clear and compelling keywords relevant to the content of the report.
            **Separate the title and the report body with a line break (\n).**
            2. The body of the report should follow this logical structure:
            - Introduction: Briefly introduce the main topic or objective of the report.
            - Main Content: Provide key insights, patterns, or analysis. Use specific data or examples to support your points.
            - Conclusion: Summarize the most important findings and restate the key points.
            3. Maintain an analytical, objective tone throughout the report. Use specific figures and data to lend credibility.
            4. The report must be written in **Korean**.

            **Important**: If the title exceeds the word or character limit, or if the report does not adhere to the above structure, it will be considered invalid.

            Article list:
            {article_contents}

            Report:
            """
        ]





        # 보고서를 저장할 리스트
        reports = []
        report_titles = []
        report_contents = []

        # 각 프롬프트로 보고서 생성
        for i, prompt_text in enumerate(prompt_text_templates):
            # OpenAI API 호출
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for analyzing and summarizing news articles."},
                    {"role": "user", "content": prompt_text}
                ],
                max_tokens=2500,
                temperature=0.65
            )

            # 응답 유효성 확인
            response_content = response['choices'][0].get('message', {}).get('content', '').strip()
            if not response_content:
                raise ValueError(f"프롬프트 {i+1}의 OpenAI 응답에서 유효한 내용을 찾을 수 없습니다.")

            # 보고서를 저장
            reports.append(response_content)

            # 제목과 본문 분리
            title_end_idx = response_content.find("\n")
            report_title = response_content[:title_end_idx].strip()
            report_content = response_content[title_end_idx:].strip()

            report_titles.append(report_title)
            report_contents.append(report_content)

            # **디버깅용 출력** - 제목 확인
            print(f"프롬프트 {i+1}로 생성된 제목: {report_title}")

        # 이미지 생성 텍스트
        img_txt = createReport_text(report_contents)

        # 결과 반환
        return {
            "reports": reports,
            "titles": report_titles,
            "img_txt": img_txt
        }

    except Exception as e:
        print(f"보고서 생성 중 에러 발생: {e}")
        return {"error": str(e)}
