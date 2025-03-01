from flask import Flask, render_template, jsonify
import requests
import textwrap
from deep_translator import GoogleTranslator  # 🔹 deep_translator 사용

# 🔹 Flask 앱 생성
app = Flask(__name__)

# 🔹 API 키
API_KEY = "b826df4bce2040e3bd600d38a8e063d5"

def fetch_news(query, sort_by):
    """
    특정 검색어(query)로 NewsAPI에서 뉴스 가져오기
    - sort_by: 'publishedAt' (최신순) 또는 'popularity' (인기순)
    """
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy={sort_by}&apiKey={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json().get("articles", [])  # 성공하면 기사 리스트 반환
    else:
        print(f"❌ API 요청 실패! 상태 코드: {response.status_code}")
        return []

def merge_news(latest_news, popular_news):
    """
    최신순(news_latest)과 인기순(news_popular) 뉴스 합치기 (중복 제거)
    """
    seen_urls = set()
    combined_articles = []

    for article in latest_news + popular_news:
        if article["url"] not in seen_urls:  # 중복 기사 제거
            seen_urls.add(article["url"])
            combined_articles.append(article)

    return combined_articles

def simple_summarize(text, max_lines=3, max_chars=200):
    """
    텍스트를 간단히 요약 (textwrap 사용, nltk 없이 처리)
    - max_lines: 최대 문장 수
    - max_chars: 최대 문자 수
    """
    if not text or len(text.split()) < 10:  # 본문이 너무 짧으면 요약하지 않음
        return "기사 내용이 부족하여 요약할 수 없습니다."

    # 문장을 최대 문자 수만큼 줄이기
    wrapped_text = textwrap.fill(text, width=max_chars)

    # 최대 문장 수만큼 나누기
    summarized_text = "\n".join(wrapped_text.split("\n")[:max_lines])

    return summarized_text

def translate_to_korean(text):
    """
    영어 텍스트를 한글로 번역 (deep_translator 사용)
    """
    try:
        return GoogleTranslator(source="en", target="ko").translate(text)
    except Exception as e:
        print(f"번역 오류: {e}")
        return "번역할 수 없습니다."

@app.route("/")
def home():
    """
    웹사이트에서 'OpenAI' 관련 뉴스 리스트를 보여주는 페이지
    """
    query = "OpenAI"  # 🔹 검색어를 'OpenAI'로 변경
    latest_news = fetch_news(query, "publishedAt")
    popular_news = fetch_news(query, "popularity")

    combined_news = merge_news(latest_news, popular_news)
    ai_filtered_news = combined_news[:5]  # 상위 5개 뉴스만 표시

    # 뉴스 본문 요약 + 한글 번역 추가
    for article in ai_filtered_news:
        summary = simple_summarize(article.get("description", ""))  # 요약 추가
        article["summary"] = summary
        article["summary_ko"] = translate_to_korean(summary)  # 🔹 한글 번역 추가

    return render_template("index.html", articles=ai_filtered_news)

if __name__ == "__main__":
    app.run(debug=True)  # 🔥 Flask 웹 서버 실행
