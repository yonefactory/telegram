import requests
from bs4 import BeautifulSoup
from transformers import BartForConditionalGeneration, BartTokenizer
import os
import feedparser

# Telegram 봇 정보
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_GROUP_CHAT_ID = os.getenv("TELEGRAM_GROUP_CHAT_ID")

# KoBART 모델과 토크나이저 로딩 (공개된 KoBART 모델 사용)
model = BartForConditionalGeneration.from_pretrained('gogamza/kobart-base-v2', num_labels=2)
tokenizer = BartTokenizer.from_pretrained('gogamza/kobart-base-v2')

def fetch_article_content(url):
    """기사 URL에서 본문 내용을 크롤링하고 리턴"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 기사 본문이 있는 태그를 찾아서 텍스트를 반환 (연합뉴스 기사 본문 div class 예시)
    paragraphs = soup.find_all('div', {'class': 'news_body'})
    content = ' '.join([para.get_text() for para in paragraphs])

    return content

def summarize_text(text):
    """기사 요약"""
    # 줄 바꿈 문자 제거
    text = text.replace('\n', ' ').replace('\r', ' ')

    # 텍스트를 인코딩하고 요약 생성
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)

    # 요약을 디코딩
    try:
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
    except KeyError as e:
        print(f"KeyError: {e}. Check the input text for problematic characters.")
        summary = "Error in summary generation."
    return summary

def get_latest_rss_news():
    """연합뉴스 RSS 피드에서 최신 기사 가져오기"""
    rss_url = "https://www.yna.co.kr/rss/news.xml"
    feed = feedparser.parse(rss_url)  # RSS 피드 파싱
    
    news_list = []

    for entry in feed.entries[:5]:  # 상위 5개 기사만 가져오기
        title = entry.title
        link = entry.link
        
        # 기사 본문 크롤링
        article_content = fetch_article_content(link)
        
        # 본문 요약
        summary = summarize_text(article_content)
        
        news_list.append(f"**{title}**\n{summary}\n{link}")

    return "\n\n".join(news_list)

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
    if news:
        send_telegram_message(news)
    else:
        send_telegram_message("⚠️ 최신 뉴스를 가져오는 데 실패했습니다.")
