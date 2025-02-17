import requests
from bs4 import BeautifulSoup
from transformers import BartForConditionalGeneration, BartTokenizer
import os
import feedparser

# Telegram 봇 정보
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # GitHub Secrets에서 가져옴
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # GitHub Secrets에서 가져옴
TELEGRAM_GROUP_CHAT_ID = os.getenv("TELEGRAM_GROUP_CHAT_ID")

# KoBART 모델과 토크나이저 로딩 (사전 학습된 한국어 모델 사용)
model = BartForConditionalGeneration.from_pretrained('kykim/koBART-base')
tokenizer = BartTokenizer.from_pretrained('kykim/koBART-base')

def fetch_article_content(url):
    """기사 URL에서 본문 내용을 크롤링하고 리턴"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 기사 본문이 있는 태그를 찾아서 텍스트를 반환 (연합뉴스 기사 본문 div class 예시)
    paragraphs = soup.find_all('div', {'class': 'news_body'})
    content = ' '.join([para.get_text() for para in paragraphs])

    return content

def summarize_text(text):
    """기사 본문을 KoBART 모델을 사용하여 요약"""
    input_text = "summarize: " + text
    input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    summary_ids = model.generate(input_ids, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
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
