import requests
from bs4 import BeautifulSoup
from datetime import datetime

TOKEN = "7802394343:AAHqzzij5wD5ms_JkYN3oWz6VvICPMYJNCo"
#CHAT_ID = "7562974684"
CHAT_ID = "-4738445656"


def send_message():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"현재 시간: {current_time}"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("메시지 전송 성공!")
    else:
        print(f"메시지 전송 실패: {response.text}")

def send_news():
    # 네이버 뉴스 주요 헤드라인 크롤링
    url = "https://news.naver.com/"  # 네이버 뉴스 홈페이지
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 주요 뉴스 제목 가져오기 (class 이름이 변경될 수 있습니다. 직접 확인 후 수정)
    headlines = soup.find_all('a', {'class': 'cluster_text_headline'})
    top_headlines = [headline.get_text(strip=True) for headline in headlines[:5]]  # 상위 5개 뉴스 제목
    
    # 텔레그램 메시지 내용
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"오늘의 주요 뉴스 ({current_time}):\n\n"
    for idx, headline in enumerate(top_headlines, 1):
        message += f"{idx}. {headline}\n"
    
    # 텔레그램 메시지 보내기
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.get(url, params=params)

if __name__ == "__main__":
    send_news()
