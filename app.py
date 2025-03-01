from flask import Flask, render_template, jsonify
import requests

# 🔹 Flask 앱 생성
app = Flask(__name__)

# 🔹 API 키
API_KEY = "b826df4bce2040e3bd600d38a8e063d5"

def filter_ai_news(articles):
    """
    뉴스 기사에서 AI 관련 키워드가 포함된 기사만 필터링
    """
    ai_keywords = ["artificial intelligence", "AI", "machine learning", "deep learning", "neural network", "OpenAI", "ChatGPT"]
    
    filtered_articles = [
        article for article in articles
        if any(keyword.lower() in article["title"].lower() for keyword in ai_keywords)
    ]
    
    return filtered_articles

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

@app.route("/")
def home():
    query = "Open Ai"
    latest_news = fetch_news(query, "publishedAt")
    popular_news = fetch_news(query, "popularity")

    combined_news = merge_news(latest_news, popular_news)
    ai_filtered_news = filter_ai_news(combined_news)  # ✅ AI 관련 기사만 필터링

    return render_template("index.html", articles=ai_filtered_news[:5])
if __name__ == "__main__":
    app.run(debug=True)  # 🔥 Flask 웹 서버 실행
