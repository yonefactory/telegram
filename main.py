import requests

BOT_TOKEN = "your_telegram_bot_token"
CHAT_ID = "your_chat_id"

def send_message():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "Hello from GitHub Actions!"}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Failed to send message: {response.text}")

if __name__ == "__main__":
    send_message()
