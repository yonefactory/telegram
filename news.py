import requests
import os
import feedparser
import json

# Telegram 봇 정보
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_GROUP_CHAT_ID = os.getenv("TELEGRAM_GROUP_CHAT_ID")

# 보낸 뉴스 저장 파일
NEWS_CACHE_FILE = "sent_news_cache.json"

# Telegram 메시지 길이 제한 (4096자)
TELEGRAM_MESSAGE_LIMIT = 4000  # 안전하게 4000자로 제한

# 보관할 뉴스 개수 (이 개수를 초과하면 오래된 뉴스 삭제)
MAX_NEWS_HISTORY = 50

def load_sent_news():
    """이전에 보낸 뉴스 목록 불러오기 (없으면 자동 생성)"""
    if not os.path.exists(NEWS_CACHE_FILE):
        print("📂 JSON 파일이 존재하지 않습니다. 새로 생성합니다.")
        save_sent_news([])  # JSON 파일 자동 생성 (빈 리스트 저장)
    
    try:
        with open(NEWS_CACHE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("❌ JSON 파일이 손상되었습니다. 초기화합니다.")
        save_sent_news([])  # JSON 파일 초기화
        return []

def save_sent_news(news_list):
    """보낸 뉴스 목록 저장 (최대 MAX_NEWS_HISTORY 개 유지)"""
    try:
        with open(NEWS_CACHE_FILE, "w", encoding="utf-8") as file:
            json.dump(news_list[-MAX_NEWS_HISTORY:], file, ensure_ascii=False, indent=4)

        # ✅ 디버깅 코드 추가: 저장된 뉴스 개수 출력
        print("\n📂 JSON 파일 저장 완료!")
        print(f"✅ 저장된 뉴스 개수: {len(news_list[-MAX_NEWS_HISTORY:])}")
        if news_list:
            print(f"📰 첫 번째 뉴스: {news_list[0]['title']} ({news_list[0]['link']})")
        print("================================\n")
    except Exception as e:
        print(f"❌ JSON 파일 저장 중 오류 발생: {e}")

def debug_show_sent_news():
    """JSON 파일에 저장된 뉴스 목록 출력 (디버깅용)"""
    sent_news = load_sent_news()
    print("\n===== 📂 저장된 뉴스 목록 (sent_news_cache.json) =====")
    if sent_news:
        for i, news in enumerate(sent_news, 1):
            print(f"{i}. {news['title']} ({news['link']})")
    else:
        print("📂 저장된 뉴스가 없습니다.")
    print("================================\n")

def get_latest_rss_news():
    """연합뉴스 RSS 피드에서 새로운 기사 가져오기"""
    rss_url = "https://www.yna.co.kr/rss/news.xml"
    feed = feedparser.parse(rss_url)  # RSS 피드 파싱

    sent_news = load_sent_news()  # 보낸 뉴스 목록 불러오기
    new_news_list = []
    updated_news_list = sent_news.copy()  # 기존 보낸 뉴스 목록 복사 (추후 업데이트)

    for entry in feed.entries:
        title = entry.title
        link = entry.link
        news_item = {"title": title, "link": link}

        # 기존에 보낸 뉴스인지 확인
        if news_item not in sent_news:
            new_news_list.append(f"🔹 **{title}**\n{link}")
            updated_news_list.append(news_item)  # 새 뉴스 추가

    # 새로운 뉴스가 있을 경우, 보낸 뉴스 목록 업데이트
    if new_news_list:
        save_sent_news(updated_news_list)

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
    debug_show_sent_news()  # ✅ JSON 파일에 저장된 뉴스 목록 출력

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
