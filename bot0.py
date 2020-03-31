import os
import telebot
import redis
import json

REDIS_URL = os.environ.get('REDIS_URL')
dict_db = {}


def save(key, value):
    if REDIS_URL:
        redis_db = redis.from_url(REDIS_URL)
        redis_db.set(key, value)
    else:
        dict_db[key] = value


def load(key, value):
    if REDIS_URL:
        redis_db = redis.from_url(REDIS_URL)
        return redis_db.get(key)
    else:
        return dict_db.get(key)


token = os.environ["TELEGRAM_TOKEN"]

bot = telebot.TeleBot(token)

IS_HEROKU = os.environ.get('IS_HEROKU', False)


# MAIN_STATE = 'main'
# DATE_STATE = 'date_state'


@bot.message_handler(content_types=['text'])
def start(message):
    # save('state:{user_id}'.format(user_id=message.from_user.id), MAIN_STATE)
    # save(str(message.from_user.id), MAIN_STATE)
    # user_state = load('state:{user_id}'.format(user_id=message.from_user.id))
    # user_state = str(message.from_user.id)
    #
    #   my_dict = {'a':10, 'b': 'xyz'}
    #
    #   save('key', my_dict)
    #
    #  my_dict_str = json.dumps(my_dict)
    #   save('key', my_dict_str)
    #  my_dict = json.loads(load('key'))
    if IS_HEROKU:
        bot.send_message(message.from_user.id, 'Я на heroku, вероятно создатель теперь '
                                               'не полный ебанат в проганьи\n' + str(REDIS_URL))

    if message.text == '/start':
        bot.send_message(message.from_user.id, 'Я подопытный кролик')


if __name__ == '__main__':
    bot.polling()
