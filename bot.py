import requests
import telegram
from environs import Env


def verification_information(devman_token, telegram_token, chat_id):
    headers = {
        "Authorization": f"Token {devman_token}",
    }
    url = "https://dvmn.org/api/long_polling/"
    params = {
        "timestamp" : None,
    }
    response = requests.get(url, headers=headers, params=params, timeout=120)
    response.raise_for_status()
    new_attempts = response.json()
    if new_attempts['status'] == 'found':
        params['timestamp'] = new_attempts['last_attempt_timestamp']
        attempts = new_attempts['new_attempts'][0]
        message = f"Преподаватель проверил работу «{attempts['lesson_title']}» {attempts['lesson_url']}.\n"
        if attempts['is_negative'] == True:
            message += "К сожалению в работе нашлись ошибки"
        else:
            message += "Преподавтелю все понравилось, можете приступать к следующему уроку"
        bot = telegram.Bot(token=telegram_token)
        bot.send_message(chat_id=chat_id, text=message)
    else:
        params['timestamp'] = new_attempts['timestamp_to_request']


def main():
    env = Env()
    env.read_env()
    devman_token = env.str('DEVMAN_TOKEN')
    telegram_token = env.str('TELEGRAM_TOKEN')
    chat_id = env.str('CHAT_ID')

    while True:
        try:
            verification_information(devman_token, telegram_token, chat_id)
        except requests.exceptions.ReadTimeout:
            print("Ожидание ответа сервера")
        except requests.exceptions.ConnectionError:
            print("Проверьте интернет соединение")


if __name__ == '__main__':
    main()
