import requests
from bs4 import BeautifulSoup
import os

# Telegram 봇 정보
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # GitHub Secrets에서 가져옴
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # GitHub Secrets에서 가져옴
NEWS_URL = "https://news.ycombinator.com/"  # Hacker News 예시

def get_latest_news():
    """Hacker News에서 최신 뉴스 제목과 링크 가져오기"""
    response = requests.get(NEWS_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    news_items = []
    for item in soup.select(".titleline a")[:5]:  # 상위 5개 뉴스 가져오기
        title = item.text
        link = item.get("href")
        news_items.append(f"🔹 {title}\n🔗 {link}")

    return "\n\n".join(news_items)

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
    news = get_latest_news()
    if news:
        send_telegram_message(news)
    else:
        send_telegram_message("⚠️ 최신 뉴스를 가져오는 데 실패했습니다.")
