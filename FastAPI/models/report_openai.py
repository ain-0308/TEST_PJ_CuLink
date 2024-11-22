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
            
            It's your job to read articles from multiple disciplines and build reports based on those articles that provide detailed analysis focusing on notable patterns, numbers, and insights.

            Here are a few things to keep in mind when creating a report:
            1. **On the first line, write a concise title that represents the report. The title must meet the following strict conditions:**
            - The title must be no longer than **15 words** or **50 characters**.
            - If the title exceeds either limit, the report will be invalidated. Adherence to this rule is critical.
            - Use clear, impactful keywords related to the report content.
            - **Use a line break (\n) to separate the title from the body of the report.**

            2. The body of the report should follow this logical structure:
            - Introduction: Briefly explain the main topic or focus.
            - Main Content: Analyze patterns, numbers, or insights, and use specific examples or data to support your points.
            - Conclusion: Summarize key takeaways and emphasize the main points clearly.
            
            3. Maintain an analytical and objective tone, and include data or figures for credibility.
            4. The report must be written in **Korean**.

            **Important**: Follow the above guidelines carefully, especially regarding the title length. Reports with titles exceeding 15 words or 50 characters will be invalidated.

            Article list:
            {article_contents}

            Report:
            """,
            f"""
            As an expert analyst, your task is to create insightful reports based on the articles provided.

            The articles include information about key trends, patterns, or challenges. Your job is to synthesize this information into a report. Remember to:
            1. **Write a concise, impactful, one-line title at the start of the report. Adhere strictly to the following rules:**
            - The title must not exceed **15 words** or **50 characters**.
            - Titles longer than this will render the report invalid. Adherence is critical.
            - Use compelling and relevant keywords summarizing the report.
            - **Use a line break (\n) to separate the title from the body of the report.**

            2. Organize the body logically in this sequence:
            - Introduction: Briefly introduce the topic or objective.
            - Main Content: Provide detailed analysis, data, or examples to support insights.
            - Conclusion: Summarize findings and emphasize key insights clearly.
            
            3. Maintain professionalism and objectivity, citing specific figures or patterns when necessary.
            4. **Write your report in Korean.**

            **Important**: The title must align with the article's content and adhere to the length limits. Reports failing this requirement will be invalidated.

            Article list:
            {article_contents}

            Report:
            """,
            f"""
            You're a skilled analyst and report writer. Your task is to identify key takeaways from multiple articles and draw actionable insights to create a compelling report.

            Based on the following articles, your report must follow these rules:
            1. **Start with a concise title that summarizes the report in one sentence. Follow these strict guidelines:**
            - The title must be no longer than **15 words** or **50 characters**.
            - Titles exceeding this limit will invalidate the report. Adherence is mandatory.
            - The title should capture the essence of the report using precise, compelling keywords.
            - **Use a line break (\n) to separate the title from the body of the report.**

            2. Write the body logically and clearly:
            - Introduction: Provide an overview of the main focus.
            - Main Content: Highlight notable patterns, figures, or data points from the articles.
            - Conclusion: Reiterate the key findings and summarize the report succinctly.

            3. Write in an analytical tone, including specific data or examples for credibility.
            4. The report must be written in **Korean**.

            **Important**: Ensure the title complies with the word and character limits. Reports that violate these rules will be considered invalid.

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
