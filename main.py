import requests
from bs4 import BeautifulSoup
from enum import Enum, auto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from environs import Env
from textwrap import dedent


class BotStates(Enum):
    START = auto()
    CHOSE_RES = auto()
    AWAIT_SONG = auto()


def start(update, context):
    update.message.reply_text(
        dedent(f'''
        Привет! Напиши название песни, а я попробую ее найти.
        '''))

    return BotStates.AWAIT_SONG


def send_song(update, context):
    song = update.message.text

    payload = {
        'do': 'search',
        'subaction': 'search',
        'story': song
    }
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    url = f'http://ru.drivemusic.me/'
    response = requests.get(url=url, params=payload, headers=headers)
    response.raise_for_status()
    page_content = BeautifulSoup(response.text, 'lxml')
    links = page_content.find_all('a', class_='popular-play__item')
    for link in links[:3]:
        context.bot.send_audio(
            chat_id=update.message.chat_id,
            audio=link.get('data-url')
        )

    return BotStates.AWAIT_SONG


def main():
    env = Env()
    env.read_env()
    telegram_token = env.str('TG_TOKEN')

    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher

    voice_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
        ],
        states={
            BotStates.START: [
                CommandHandler('start', start)
            ],
            BotStates.AWAIT_SONG: [
                MessageHandler(Filters.text, send_song),
            ],
        },

        per_user=True,
        per_chat=True,
        fallbacks=[],
    )

    dispatcher.add_handler(voice_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

