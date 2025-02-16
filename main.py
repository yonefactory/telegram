import requests
from datetime import datetime

BOT_TOKEN = "7802394343:AAHqzzij5wD5ms_JkYN3oWz6VvICPMYJNCo"
#CHAT_ID = "7562974684"
CHAT_ID = -4738445656"
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

if __name__ == "__main__":
    send_message()
