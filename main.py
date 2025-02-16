import requests
from bs4 import BeautifulSoup
from datetime import datetime

BOT_TOKEN = "7802394343:AAHqzzij5wD5ms_JkYN3oWz6VvICPMYJNCo"
#CHAT_ID = "7562974684"
CHAT_ID = "-4738445656"


def send_message():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"현재 시간: {current_time}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("메시지 전송 성공!")
    else:
        print(f"메시지 전송 실패: {response.text}")

def send_news():

    # 뉴스 웹사이트에서 주요 뉴스 크롤링
    url = "https://news.ycombinator.com/"  # 예시: Hacker News
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 뉴스 제목 가져오기 (예시)
    headlines = soup.find_all('a', class_='storylink')
    top_headlines = [headline.get_text() for headline in headlines[:5]]  # 상위 5개 뉴스 제목
    
    # 텔레그램 메시지 내용
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"오늘의 주요 뉴스 ({current_time}):\n\n"
    for idx, headline in enumerate(top_headlines, 1):
        message += f"{idx}. {headline}\n"
    
    # 텔레그램 메시지 보내기
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.get(url, params=params)

if __name__ == "__main__":
    send_news()
