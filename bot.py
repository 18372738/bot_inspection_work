import requests
import telegram
from environs import Env
from time import sleep


env = Env()
env.read_env()

DEVMAN_TOKEN = env.str('DEVMAN_TOKEN')
TELEGRAM_TOKEN = env.str('TELEGRAM_TOKEN')
CHAT_ID = env.str('CHAT_ID')


def send_message(attempt):
    message = f"Преподаватель проверил работу «{attempt['lesson_title']}» {attempt['lesson_url']}.\n"
    if attempt['is_negative']:
        message += "К сожалению в работе нашлись ошибки"
    else:
        message += "Преподавтелю все понравилось, можете приступать к следующему уроку"
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    headers = {
        "Authorization": f"Token {DEVMAN_TOKEN}",
    }
    url = "https://dvmn.org/api/long_polling/"
    params = {
        "timestamp" : None,
    }
    while True:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=120)
            response.raise_for_status()
            new_attempts = response.json()
            if new_attempts['status'] == 'found':
                params['timestamp'] = new_attempts['last_attempt_timestamp']
                attempt = new_attempts['new_attempts'][0]
                send_message(attempt)
            else:
                params['timestamp'] = new_attempts['timestamp_to_request']
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            print("Проверьте интернет соединение")
            time.sleep(10)


if __name__ == '__main__':
    main()
