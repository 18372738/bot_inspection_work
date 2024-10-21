import logging
import requests
import telegram
from environs import Env
from time import sleep


class TelegramLogsHandler(logging.Handler):

    def __init__(self, bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.bot = bot

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)


def send_message(attempt, telegram_token, chat_id):
    message = f"Преподаватель проверил работу «{attempt['lesson_title']}» {attempt['lesson_url']}.\n"
    if attempt['is_negative']:
        message += "К сожалению в работе нашлись ошибки"
    else:
        message += "Преподавтелю все понравилось, можете приступать к следующему уроку"
    bot = telegram.Bot(token=telegram_token)
    bot.send_message(chat_id=chat_id, text=message)


def main():
    env = Env()
    env.read_env()

    logging.basicConfig(format="%(process)d %(levelname)s %(message)s")
    logger = logging.getLogger('telegram_logger')
    logger.setLevel(logging.INFO)

    devman_token = env.str('DEVMAN_TOKEN')
    telegram_token = env.str('TELEGRAM_TOKEN')
    telegram_logger = env.str('TELEGRAM_LOGGER')
    chat_id = env.str('CHAT_ID')
    headers = {
        "Authorization": f"Token {devman_token}",
    }
    url = "https://dvmn.org/api/long_polling/"
    params = {
        "timestamp" : None,
    }
    bot = telegram.Bot(token=telegram_logger)

    logger.addHandler(TelegramLogsHandler(bot, chat_id))
    logger.info("Бот запущен и ожидает проверок...")

    while True:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=120)
            response.raise_for_status()
            new_attempts = response.json()
            if new_attempts['status'] == 'found':
                params['timestamp'] = new_attempts['last_attempt_timestamp']
                attempt = new_attempts['new_attempts'][0]
                send_message(attempt, telegram_token, chat_id)
            else:
                params['timestamp'] = new_attempts['timestamp_to_request']
        except requests.ReadTimeout:
            continue
        except requests.ConnectionError:
            logger.warning("Нет интернет соединения.")
            time.sleep(10)
        except Exception as error:
            logger.error(f'Бот упал с ошибкой:\n{error}')


if __name__ == '__main__':
    main()
