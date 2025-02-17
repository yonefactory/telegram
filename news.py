import requests
from bs4 import BeautifulSoup
import os
import random

# Telegram 봇 정보
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # GitHub Secrets에서 가져옴
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # GitHub Secrets에서 가져옴

def get_latest_news():
    NEWS_URL = "https://news.ycombinator.com/"  # Hacker News 예시
    
    """Hacker News에서 최신 뉴스 제목과 링크 가져오기"""
    response = requests.get(NEWS_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    news_items = []
    for item in soup.select(".titleline a")[:5]:  # 상위 5개 뉴스 가져오기
        title = item.text
        link = item.get("href")
        news_items.append(f"🔹 {title}\n🔗 {link}")

    return "\n\n".join(news_items)

def get_latest_korean_news():
    """한국 주요 뉴스 5개 가져오기"""
    url = "https://news.naver.com/main/home.naver"  # 네이버 뉴스 메인 페이지

    # User-Agent 목록
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
    ]

    # 랜덤 User-Agent 헤더 설정
    headers = {
        "User-Agent": random.choice(USER_AGENTS)
    }

    # 프록시 리스트
    proxies_list = [
        {"http": "http://5.78.124.240:40000", "https": "http://5.78.124.240:40000"},
        {"http": "http://222.252.194.204:8080", "https": "http://222.252.194.204:8080"},
        {"http": "http://85.215.64.49:80", "https": "http://85.215.64.49:80"},
        {"http": "http://72.10.160.170:5475", "https": "http://72.10.160.170:5475"},
        {"http": "http://50.223.246.23:80", "https": "http://50.223.246.23:80"},
        {"http": "http://50.174.7.159:80", "https": "http://50.174.7.159:80"},
        {"http": "http://41.207.187.178:80", "https": "http://41.207.187.178:80"},
    ]
    
    # 랜덤으로 프록시 선택
    proxy = random.choice(proxies_list)
    
    response = requests.get(url, headers=headers, proxies=proxies)

    if response.status_code != 200:
        print(f"Failed to fetch news: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # 주요 뉴스 섹션에서 뉴스 제목 및 링크 가져오기
    news_list = []
    headlines = soup.select(".hdline_article_tit a")[:5]  # 상위 5개 뉴스
    for headline in headlines:
        title = headline.text.strip()
        link = headline["href"]
        if not link.startswith("http"):
            link = "https://news.naver.com" + link
        news_list.append(f"{title}\n{link}")
    
    return news_list

def send_telegram_message(message):
    """Telegram 봇으로 메시지 전송"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": True,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data)
    return response.json()

if __name__ == "__main__":
    news = get_latest_korean_news()
    if news:
        send_telegram_message(news)
    else:
        send_telegram_message("⚠️ 최신 뉴스를 가져오는 데 실패했습니다.")
