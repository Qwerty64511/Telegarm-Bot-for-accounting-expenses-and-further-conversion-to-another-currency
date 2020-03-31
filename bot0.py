import os
import telebot

token = os.environ["TELEGRAM_TOKEN"]


bot = telebot.TeleBot(token)


HEROKU = os.environ.get('HEROKU', False)


@bot.message_handler(content_types=['text'])
def start(message):
    if HEROKU:
        bot.send_message(message.from_user.id, 'Я на heroku, вероятно создатель теперь не полный ебанат в проганьи')

    if message.text == '/start':
        bot.send_message(message.from_user.id, 'Я подопытный кролик')


if __name__ == '__main__':
    bot.polling()
