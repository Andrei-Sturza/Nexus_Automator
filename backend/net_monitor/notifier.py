import requests

#Token of the bot
BOT_TOKEN = '8012321807:AAHweykA591mvHuZMF7_yqgRoPKJPt79H5k'

#ID of the chat that we want the bot to send the message
CHAT_ID = '-1002362075038'

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Failed to send alert: {e}")
