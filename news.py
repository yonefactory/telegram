import requests
import os
import feedparser
import json

# Telegram 봇 정보
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_GROUP_CHAT_ID = os.getenv("TELEGRAM_GROUP_CHAT_ID")

# 이전에 보낸 뉴스 저장 파일
NEWS_CACHE_FILE = "sent_news_cache.json"

def load_sent_news():
    """이전에 보낸 뉴스 목록 불러오기"""
    if os.path.exists(NEWS_CACHE_FILE):
        with open(NEWS_CACHE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_sent_news(news_list):
    """보낸 뉴스 목록 저장"""
    with open(NEWS_CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(news_list, file, ensure_ascii=False, indent=4)

def get_latest_rss_news():
    """연합뉴스 RSS 피드에서 새로운 기사 가져오기"""
    rss_url = "https://www.yna.co.kr/rss/news.xml"
    feed = feedparser.parse(rss_url)  # RSS 피드 파싱

    sent_news = load_sent_news()  # 이전에 보낸 뉴스 로드
    new_news_list = []

    for entry in feed.entries:
        title = entry.title
        link = entry.link
        
        # 이미 보낸 뉴스인지 확인
        if link not in sent_news:
            new_news_list.append(f"🔹 **{title}**\n🔗 [기사 보기]({link})")
            sent_news.append(link)

    # 보낸 뉴스 기록 업데이트
    if new_news_list:
        save_sent_news(sent_news)

    return "\n\n".join(new_news_list)

def send_telegram_message(message):
    """Telegram 봇으로 메시지 전송"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_GROUP_CHAT_ID,
        "text": message,
        "disable_web_page_preview": True,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data)
    return response.json()

if __name__ == "__main__":
    news = get_latest_rss_news()
    
    if news:  # 새로운 뉴스가 있을 경우만 전송
        send_telegram_message(f"📰 **오늘의 최신 뉴스**\n\n{news}")
