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

# Telegram 메시지 길이 제한 (4096자)
TELEGRAM_MESSAGE_LIMIT = 4000  # 안전하게 4000자로 제한

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
            new_news_list.append(f"🔹 **{title}**\n{link}")
            sent_news.append(link)

    # 보낸 뉴스 기록 업데이트
    if new_news_list:
        save_sent_news(sent_news)

    return new_news_list

def split_message(messages):
    """Telegram 메시지 길이 제한을 고려하여 분할"""
    chunks = []
    current_chunk = "📢 **실시간 뉴스 업데이트**\n\n"
    
    for msg in messages:
        if len(current_chunk) + len(msg) + 2 > TELEGRAM_MESSAGE_LIMIT:
            chunks.append(current_chunk)
            current_chunk = "📢 **실시간 뉴스 업데이트**\n\n"
        
        current_chunk += msg + "\n\n"

    if current_chunk.strip():
        chunks.append(current_chunk)

    return chunks

def send_telegram_message(message):
    """Telegram 봇으로 메시지 전송 후 응답 확인"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_GROUP_CHAT_ID,
        "text": message,
        "disable_web_page_preview": True,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data)
    
    # ✅ 디버깅 코드 추가: 응답 상태 확인
    if response.status_code == 200:
        print("✅ Telegram 메시지 전송 성공!")
    else:
        print("❌ Telegram 메시지 전송 실패!")
        print("🔍 응답 코드:", response.status_code)
        print("📌 응답 내용:", response.text)

    return response.json()

if __name__ == "__main__":
    news_list = get_latest_rss_news()
    
    if news_list:  # 새로운 뉴스가 있을 경우만 전송
        news_chunks = split_message(news_list)  # 메시지 길이에 맞게 분할
        
        # ✅ 디버깅 코드 추가: 전송 전 터미널 출력
        for i, chunk in enumerate(news_chunks, 1):
            print(f"\n===== 📰 전송할 뉴스 목록 (Part {i}) =====")
            print(chunk)
            print("================================\n")
        
        # ✅ Telegram 메시지 분할 전송
        for chunk in news_chunks:
            send_telegram_message(chunk)
    
    else:
        print("🔍 새로운 뉴스가 없습니다. 전송하지 않습니다.")
