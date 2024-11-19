import openai
from langchain_community.llms import OpenAI
from models.textToImage import generate_images_and_send
from db.settings import openai_key

# API 키 설정
openai.api_key = openai_key  # OpenAI API 키

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
            You're a skilled analyst and report writer, and your role is to identify key takeaways from multiple articles and draw new insights from them to create a report.

            Based on the following articles, you've identified important information, common issues, or noteworthy patterns that will provide new perspectives and analysis. The title of the report should be on the first line, and the body of the report should flow naturally with no line breaks.

            Here are a few things to keep in mind when creating a report:
            1. **On the first line, write a concise title that is representative of the report. The title should be no longer than 15 words or 50 characters. **This is a very important requirement and must be adhered to as the entire report will be invalidated if the title exceeds 15 words. Write a clear and compelling title using keywords that are relevant to the content of the report.
              **Use line breaks(\n) to separate the title from the body of the report.**
            2. The body of the report should be logically and smoothly organized in the following order: introduction, body, conclusion, without subheadings.
            3. If you have specific figures or examples in your writing, use them to substantiate your insights.
            4. Maintain an analytical, objective tone and include specific figures or data to lend credibility to your report.
            5. At the end of your report, emphasize the most important points of your topic by restating them.
            6. **Write your report in Korean.**

            **Important** : Make sure to follow the above guidelines when writing your report, as failure to do so will invalidate your report.
            Article list:

            {article_contents}

            Report:
            """,
            f"""
            As an expert analyst, your job is to create insightful reports based on the following articles.

            The articles contain information about key trends, patterns, or common issues. Your report should synthesize these insights into a comprehensive and compelling report. The title should appear on the first line, and the body should flow naturally without line breaks or subheadings.


            Remember:
            1. **Write a concise, impactful, one-line title as the first line of the report. The title should be 20 words or less. Reports with titles longer than 20 words will be invalidated. Focus on using keywords that summarize the report to make the title clear and compelling.
              **Use line breaks(\n) to separate the title from the body of the report.**
            2. The body of the report should be logically organized in the following order: introduction, main content, and conclusion.
            3. Maintain a professional tone by using specific examples, figures, or patterns observed in the article.
            4. Include a concise summary of the most important findings in the conclusion of your report.
            5. Write your report in Korean.

            **Warning: Please make sure your title complies with the word count limit, as failure to do so will invalidate your report.

            Article list:
            {article_contents}

            Report:
            """,
            f"""
            You need to create a professional report based on multiple articles. The report should provide a detailed analysis that focuses on noteworthy patterns, figures, and insights.

            Key points to remember
            1. **The report begins with a concise title that summarizes the report in one sentence. This title should be no longer than 15 words or 50 characters.** If the title is longer than 15 words, the report is considered invalid, so be sure to stick to the word limit. The title should emphasize the main content of the report and grab attention.
              **Use line breaks(\n) to separate the title from the body of the report.**
            2. The body of the report should follow a logical structure from introduction to main points to conclusion.
            3. Cite specific data or examples to support your analysis where relevant.
            4. 4. Conclude the report by summarizing the main points.
            5. **Write the report in Korean.**

             **IMPORTANT** : Reports that do not follow the above key points will not be valid. Please make sure to follow the above key points when writing your report.

            Article list:
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
