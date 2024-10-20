import logging
import requests
import telegram
from environs import Env
from time import sleep


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO


def send_message(attempt, telegram_token, chat_id):
    message = f"Преподаватель проверил работу «{attempt['lesson_title']}» {attempt['lesson_url']}.\n"
    if attempt['is_negative']:
        message += "К сожалению в работе нашлись ошибки"
    else:
        message += "Преподавтелю все понравилось, можете приступать к следующему уроку"
    bot = telegram.Bot(token=telegram_token)
    logging.info(f"Отправка сообщения о проверке урока {attempt['lesson_title']}")
    bot.send_message(chat_id=chat_id, text=message)


def main():
    env = Env()
    env.read_env()

    devman_token = env.str('DEVMAN_TOKEN')
    telegram_token = env.str('TELEGRAM_TOKEN')
    chat_id = env.str('CHAT_ID')

    headers = {
        "Authorization": f"Token {devman_token}",
    }
    url = "https://dvmn.org/api/long_polling/"
    params = {
        "timestamp" : None,
    }

    logging.info("Бот запущен и ожидает проверок...")

    while True:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=120)
            response.raise_for_status()
            new_attempts = response.json()
            if new_attempts['status'] == 'found':
                params['timestamp'] = new_attempts['last_attempt_timestamp']
                attempt = new_attempts['new_attempts'][0]
                logging.info(f"Найдена новая проверка: {attempt['lesson_title']}")
                send_message(attempt, telegram_token, chat_id)
            else:
                params['timestamp'] = new_attempts['timestamp_to_request']
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            logging.error(f"Произошла ошибка: {e}")
            time.sleep(10)


if __name__ == '__main__':
    main()
