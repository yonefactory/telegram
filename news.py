import requests
from bs4 import BeautifulSoup
from transformers import BartForConditionalGeneration, BartTokenizer
import os
import random
import feedparser

# Telegram 봇 정보
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # GitHub Secrets에서 가져옴
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # GitHub Secrets에서 가져옴
TELEGRAM_GROUP_CHAT_ID = os.getenv("TELEGRAM_GROUP_CHAT_ID")

# BART 모델과 토크나이저 로딩 (사전 학습된 모델 사용)
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')

def fetch_article_content(url):
    """기사 URL에서 본문 내용을 크롤링하고 리턴"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 기사 본문이 있는 태그를 찾아서 텍스트를 반환 (네이버, 연합뉴스 등 웹사이트마다 다를 수 있음)
    paragraphs = soup.find_all('div', {'class': 'news_body'})  # 연합뉴스 기사 본문 div class 예시
    content = ' '.join([para.get_text() for para in paragraphs])

    return content

def summarize_text(text):
    """기사 본문을 요약"""
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
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
