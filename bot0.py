import os
import telebot

token = os.environ["TELEGRAM_TOKEN"]

bot = telebot.TeleBot(token)

IS_HEROKU = os.environ.get('IS_HEROKU', False)

ADMIN = (0, 1, 2)


@bot.message_handler(content_types=['text'])
def start(message):
    if IS_HEROKU:
        bot.send_message(message.from_user.id, 'Я на heroku, вероятно создатель теперь не полный ебанат в проганьи')

    if message.text == '/start':
        bot.send_message(message.from_user.id, 'Я подопытный кролик')


if __name__ == '__main__':
    bot.polling()
