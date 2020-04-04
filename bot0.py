import redis
import os
import telebot
import json
import requests
import random
from telebot import types

token = os.environ['TELEGRAM_TOKEN']

bot = telebot.TeleBot(token)

koeficienti = {}  # будем в основном использовать на этапе с конвертацией, для коэффициентов

url = 'https://www.cbr-xml-daily.ru/daily_json.js'  # записываем в переменную url API центрабанка
response = requests.get(url).json()
USD = response['Valute']['USD']['Value']  # Из api центрабанка достали стоимость доллара в рублях
print(USD)
koeficienti[USD] = USD
koeficienti[11] = USD
EUR = response['Valute']['EUR']['Value']  # Из api центрабанка достали стоимость евро в рублях
koeficienti[0] = EUR
CNY = response['Valute']['CNY']['Value']  # Из api центрабанка достали стоимость юаней в рублях
koeficienti[1] = CNY
# Задаём коэффициенты перевода из одной валюты в другую
izEURvUSD = int(EUR) / int(USD)
koeficienti[2] = izEURvUSD
izUSDvEUR = int(USD) / int(EUR)
koeficienti[3] = izUSDvEUR
izRUBvUSD = 1 / int(USD)
koeficienti[4] = izRUBvUSD
izRUBvEUR = 1 / int(EUR)
koeficienti[5] = izRUBvEUR
izRUBvCNY = 1 / int(CNY)
koeficienti[6] = izRUBvCNY
izUSDvCNY = int(USD) / int(CNY)
koeficienti[7] = izUSDvCNY
izEURvCNY = int(EUR) / int(CNY)
koeficienti[8] = izEURvCNY
izCNYvUSD = int(CNY) / int(USD)
koeficienti[9] = izCNYvUSD
izCNYvEUR = int(CNY) / int(EUR)
koeficienti[10] = izCNYvEUR

# Вводим все состояния
MAIN_STATE = 'main'
Vvedini = 'vvedeni dannie'
Symiruem = 'idet rasschet'
SYM1 = 'vtoroe rasschitat'
konvertiruem = 'idet konvertaciya'
ADMIN = 'idet administrirovanie'
redis_url = os.environ.get('REDIS_URL')
dict_db = {}
if redis_url is None:
    try:
        data = json.load(open('db/data.json', 'r', encoding='utf-8'))  # выводим нашу базу данных
    except FileNotFoundError:
        data = {
            "states": {},
            "main": {},
            "vvedeni dannie": {},
            "idet rasschet": {},
            "vtoroe rasschitat": {},
            "idet konvertaciya": {},
            "idet administrirovanie": {},
            "sym": {},
            "konvertaciya": {},
            "Admins": {
                "mainadmins": "810391410"
            }
        }
else:
    redis_db = redis.from_url(redis_url)
    raw_data = redis_db.get('data')
    print('Viveodim')
    if raw_data is None:
        data = {
            "states": {},
            "main": {},
            "vvedeni dannie": {},
            "idet rasschet": {},
            "vtoroe rasschitat": {},
            "idet konvertaciya": {},
            "idet administrirovanie": {},
            "sym": {},
            "konvertaciya": {},
            "Admins": {
                "mainadmins": "810391410"
            }
        }
    else:
        data = json.loads(raw_data)  # выводим нашу базу данных
        print('Viveli')

konvertaciya = data['konvertaciya']  # будем использовать на этапе с конвертацией и выводом "квт", для других переменных
sym = data['sym']  # объявляем словарь с суммой


# функция изменения базы данных
def change_data(key, user_id, value):
    data[key][user_id] = value
    if redis_url is None:
        json.dump(data,
                  open('db/data.json', 'w', encoding='utf-8'),
                  indent=2,
                  ensure_ascii=False,
                  )
    else:
        redis_db = redis.from_url(redis_url)
        redis_db.set('data', json.dumps(data))


# диспетчер состояний
@bot.message_handler(content_types=['text'])
def dispatcher(message):
    user_id = str(message.from_user.id)
    if str(data['states']) == '{}':
        # проверяем наличие пользователей, если их нет,
        # то вызываем функцию добавления пользователя
        change_data('states', user_id, MAIN_STATE)
    try:
        print(data['states'][user_id])  # Проверяем наличие пользователя в БД, если его нет в БД, то добавляем его в БД
    except KeyError:
        change_data('states', user_id, MAIN_STATE)
    state = data['states'][user_id]
    print('current state', user_id, state)
    # Обрабатываем состояния
    if state == MAIN_STATE:
        main_handler(message)
    elif state == Vvedini:
        Trati(message)
    elif state == Symiruem:
        Sym(message)
    elif state == SYM1:
        Sym1(message)
    elif state == konvertiruem:
        Trati2(message)
    elif state == ADMIN:
        adminpanel(message)


# основной обработчик
def main_handler(message):
    user_id = str(message.from_user.id)
    if message.text == '/start':
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
        btn1 = types.KeyboardButton('/test')
        btn2 = types.KeyboardButton('/help')
        btn3 = types.KeyboardButton('Рассчитать')
        markup.row(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, 'Привет, я могу помочь тебе рассчитать дневные затраты, по команде '
                                               '/help '
                                               'вы узнаете возможности бота.   '
                                               'Напишите комманду /test для более понятного объяснения работы бота. '
                                               'Напишите "Рассчитать" чтобы добавить трату', reply_markup=markup)
    elif message.text == '/test':
        test(message)
    elif message.text == '/help':
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
        btn2 = types.KeyboardButton('/test')
        btn3 = types.KeyboardButton('Рассчитать')
        markup.row(btn2, btn3)
        tekct = 'По команде "рассчитать" вы вводите трату, по комманде /test вам будет представлен пример работы бота'
        bot.send_message(message.from_user.id, tekct, reply_markup=markup)
    elif message.text.lower() == 'рассчитать':
        bot.send_message(message.from_user.id, 'напиши сколько ты потратил(только цифрами)')
        change_data('states', user_id, Symiruem)
        print(str(data['states'][user_id]))
    elif message.text.lower() == 'траты' or message.text.lower() == 'квт' or message.text.lower() == 'конвертировать':
        bot.send_message(message.from_user.id, 'Вы ещё не ввели трату. Напишите "рассчитать" чтобы ввести трату')
    elif message.text.lower() == 'админ панель':
        adminpanel(message)
        doadmenki = data['states'][user_id]
        koeficienti[12] = doadmenki
        change_data('states', user_id, ADMIN)
    else:
        bot.send_message(message.from_user.id, 'Я вас не понял')


def adminpanel(message):
    user_id = str(message.from_user.id)
    admins = data["Admins"]["mainadmins"]
    if user_id in admins:
        if message.text.lower() == 'очистить бд':
            bot.send_message(message.from_user.id, 'Идёт очистка базы данных')
            ochistka(message)
        elif message.text.lower() == 'вывод бд':
            tekct0 = 'STATES:  ' + str(data['states']) + 'SYMMI:  ' + str(data['sym']) + 'Informaciya pro konvertaciyu'
            tekct1 = str(data['konvertaciya'])
            tekct = tekct0 + '  ' + tekct1
            bot.send_message(user_id, tekct)
        elif message.text.lower() == 'выход':
            doadmenki = koeficienti[12]
            change_data('states', user_id, doadmenki)
            bot.send_message(user_id, 'Выход выполнен')
        elif message.text.lower() == 'админ панель':
            bot.send_message(user_id, 'Режим администрирования')
        else:
            bot.send_message(user_id, 'Команда не верна')


def ochistka(message):
    user_id = str(message.from_user.id)
    data['states'] = {}
    data['sym'] = {}
    data['konvertaciya'] = {}
    print(data)
    change_data('states', user_id, ADMIN)
    print(data['states'])


# Пример работы бота
def test(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
    btn2 = types.KeyboardButton('/help')
    btn3 = types.KeyboardButton('Рассчитать')
    markup.row(btn2, btn3)
    tekct = ' Вы: Пишите комманду "рассчитать",\nЗатем пишите цифрами сколько вы потратили,\nПосле выбираете валюту,\n'
    tekct1 = 'Потом вы можете Получить ваши траты написав комманду "Траты"\nвам выведится значение в виде:'
    bot.send_message(message.from_user.id, tekct + tekct1)
    primersymmi = random.randrange(1000, 30000)
    primervaluti = random.choice(['Долларов', 'Рублей', 'Евро', 'Юаней'])
    soobchenie = 'Ваши траты составили: ' + str(primersymmi) + ' ' + str(primervaluti)
    bot.send_message(message.from_user.id, soobchenie, reply_markup=markup)


# записывальщик трат
def Sym(message):
    user_id = str(message.from_user.id)
    state = data['states'][user_id]
    if state == Symiruem:
        symma = 0
        cifra = message.text
        symma += int(str(cifra))
        sym[user_id] = symma
        sym["1"] = cifra
        keyboard2 = types.InlineKeyboardMarkup()
        key_eur = types.InlineKeyboardButton(text='в евро', callback_data='eunow')
        keyboard2.add(key_eur)  # добавляем кнопку в клавиатуру
        key_usd = types.InlineKeyboardButton(text='В долларах', callback_data='usnow')
        keyboard2.add(key_usd)
        key_rub = types.InlineKeyboardButton(text='В рублях', callback_data='rubnow')
        keyboard2.add(key_rub)
        key_cny = types.InlineKeyboardButton(text='В юанях', callback_data='cnynow')
        keyboard2.add(key_cny)
        question2 = 'В какой валюте вы тратили деньги?'
        bot.send_message(message.from_user.id, text=question2, reply_markup=keyboard2)


# записывальщик трат, когда уже была введена трата
def Sym1(message):
    user_id = str(message.from_user.id)
    state = data['states'][user_id]
    if state == SYM1:
        symma = int(sym[user_id])
        cifra = message.text
        symma += int(str(cifra))
        sym[user_id] = symma
        sym["1"] = cifra
        markup1 = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
        btn1 = types.KeyboardButton('Траты')
        btn2 = types.KeyboardButton('конвертировать')
        btn3 = types.KeyboardButton('Рассчитать')
        markup1.row(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, 'Хорошо, я записал вашу трату, узнать её вы можете написав команду '
                                               '"траты"', reply_markup=markup1)
        change_data('states', user_id, Vvedini)


#  функция присваивания валюты
def oprvaliuti(call, valuta):
    user_id = str(call.from_user.id)
    konvertaciya[user_id + 'valiutatrat'] = valuta


# обработчик клавиатуры
@bot.callback_query_handler(func=lambda call: True)
def valuta(call):
    user_id = str(call.from_user.id)
    state = data['states'][user_id]
    if state == Symiruem:
        # объявляем валюту
        if call.data == 'eunow':
            valiuta = 'Евро'
            oprvaliuti(call, valiuta)

        if call.data == 'usnow':
            valiuta = 'Долларах'
            oprvaliuti(call, valiuta)
        if call.data == 'rubnow':
            valiuta = 'Рублях'
            oprvaliuti(call, valiuta)
        if call.data == 'cnynow':
            valiuta = 'Юанях'
            oprvaliuti(call, valiuta)
        markup1 = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
        btn1 = types.KeyboardButton('Траты')
        btn2 = types.KeyboardButton('конвертировать')
        btn3 = types.KeyboardButton('Рассчитать')
        markup1.row(btn1, btn2, btn3)
        bot.send_message(call.message.chat.id, 'Я записал вашу валюту, узнать ваши траты и '
                                               'валюту трат вы можете по комманде "траты" '
                                               'Также вы можете конвертировать ваши траты в другую валюту написав '
                                               'комманду '
                                               '"конвертировать"', reply_markup=markup1)
        change_data('states', user_id, Vvedini)
        valiutahandler(call)  # вызываем функцию обработки переменной now

    else:
        valiutahandler(call)  # вызываем функцию обработки переменной now
        perevod(call)  # вызываем другой скрипт обработчика


def valiutahandler(call):
    user_id = str(call.from_user.id)
    valiuta = konvertaciya[user_id + 'valiutatrat']
    if 'Руб' in valiuta:
        now = 'rub'
        konvertaciya[1] = now
    if 'Дол' in valiuta:
        now = 'us'
        konvertaciya[1] = now
    if 'Евр' in valiuta:
        now = 'eu'
        konvertaciya[1] = now
    if 'Юан' in valiuta:
        now = 'cny'
        konvertaciya[1] = now


# обработчик при введённых тратах
def Trati(message):
    user_id = str(message.from_user.id)
    valiuta = konvertaciya[user_id + 'valiutatrat']
    if message.text.lower() == 'траты':
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
        btn1 = types.KeyboardButton('Рассчитать')
        btn2 = types.KeyboardButton('конвертировать')
        if str(data['states'][user_id]) == konvertiruem:
            btn3 = types.KeyboardButton('квт')
            markup.row(btn1, btn2, btn3)
        else:
            markup.row(btn1, btn2)
        symma = data['sym'][user_id]
        vivod = 'Ваши траты составили: ' + str(symma) + '  ' + 'Вы тратили деньги в ' + valiuta
        bot.send_message(message.from_user.id, vivod, reply_markup=markup)
    elif message.text.lower() == 'рассчитать':
        bot.send_message(message.from_user.id, 'напиши сколько ты потратил(только цифрами)')
        change_data('states', user_id, SYM1)
    elif message.text.lower() == 'конвертировать':
        konvert(message)
    elif message.text.lower() == 'квт':
        bot.send_message(message.from_user.id, 'Вы ещё не сконвертировали траты')
    else:
        main_handler(message)


#  обработчик при введённых данных и проделанной конвертации
def Trati2(message):
    user_id = str(message.from_user.id)
    if message.text.lower() == 'квт':
        konvertirovano = konvertaciya[user_id + 'symma']
        vochtoperevesti = konvertaciya[user_id]
        bot.send_message(message.from_user.id, 'Ваши траты: ' + str(konvertirovano) + ' ' + str(vochtoperevesti))
    else:
        Trati(message)


#  Клавиатура выбора валюты в которую конвертировать
def konvert(message):
    # создаём клавиатуру, для определения, в какую валюту переводить
    keyboard = types.InlineKeyboardMarkup()
    key_euro = types.InlineKeyboardButton(text=' перевести в Евро', callback_data='eu')
    keyboard.add(key_euro)  # добавляем кнопку в клавиатуру
    key_usd = types.InlineKeyboardButton(text='перевести в Доллары', callback_data='us')
    keyboard.add(key_usd)
    key_rub = types.InlineKeyboardButton(text='перевести в Рубли', callback_data='rub')
    keyboard.add(key_rub)
    key_cny = types.InlineKeyboardButton(text='Перевести в Юани', callback_data='cny')
    keyboard.add(key_cny)
    question = 'В какую валюту вы хотите конвертировать?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


# Конвертатор валют
@bot.callback_query_handler(func=lambda call: True)
def perevod(call):
    user_id = str(call.from_user.id)
    change_data('states', user_id, konvertiruem)
    now = konvertaciya[1]
    # обработчик клавиатуры в которой задаётся, переменная в которую мы переводим
    symma = sym[user_id]
    CNY = koeficienti[1]
    USD = koeficienti[11]
    EUR = koeficienti[0]
    izEURvUSD = koeficienti[2]
    izUSDvEUR = koeficienti[3]
    izRUBvUSD = koeficienti[4]
    izRUBvEUR = koeficienti[5]
    izRUBvCNY = koeficienti[6]
    izUSDvCNY = koeficienti[7]
    izEURvCNY = koeficienti[8]
    izCNYvUSD = koeficienti[9]
    izCNYvEUR = koeficienti[10]
    vochtoperevesti = call.data
    # всё ниже это конвертаторы из одной валюты в другую. Всё точно работает:)
    if vochtoperevesti == "eu" and now == 'eu':
        bot.send_message(call.message.chat.id, 'Ваша валюта уже евро')
    if vochtoperevesti == "rub" and now == 'rub':
        bot.send_message(call.message.chat.id, 'Ваша валюта уже рубли')
    if vochtoperevesti == "us" and now == 'us':
        bot.send_message(call.message.chat.id, 'Ваша валюта уже доллары')
    if vochtoperevesti == 'cny' and now == 'cny':
        bot.send_message(call.message.chat.id, 'Ваша валюта уже юани')
    if vochtoperevesti == 'rub' and now == 'cny':
        konvertirovano = int(symma) * CNY
        konvertaciya[user_id + 'symma'] = konvertirovano
        okryglenie(call)
        KonvertV_RUB(call)
        messkonvert(call)
    if vochtoperevesti == 'cny' and now == 'rub':
        konvertirovano = int(symma) * izRUBvCNY
        konvertaciya[user_id + 'symma'] = konvertirovano
        okryglenie(call)
        KonvertV_CNY(call)
        messkonvert(call)
    if vochtoperevesti == 'us' and now == 'cny':
        konvertirovano = int(symma) * izCNYvUSD
        konvertaciya[user_id + 'symma'] = konvertirovano
        okryglenie(call)
        KonvertV_USD(call)
        messkonvert(call)
    if vochtoperevesti == 'cny' and now == 'eu':
        konvertirovano = int(symma) * izEURvCNY
        konvertaciya[user_id + 'symma'] = konvertirovano
        okryglenie(call)
        KonvertV_CNY(call)
        messkonvert(call)
    if vochtoperevesti == 'cny' and now == 'us':
        konvertirovano = int(symma) * izUSDvCNY
        konvertaciya[user_id + 'symma'] = konvertirovano
        okryglenie(call)
        KonvertV_CNY(call)
        messkonvert(call)
    if vochtoperevesti == 'eu' and now == 'cny':
        konvertirovano = int(symma) * izCNYvEUR
        konvertaciya[user_id + 'symma'] = konvertirovano
        okryglenie(call)
        KonvertV_EUR(call)
        messkonvert(call)
    if vochtoperevesti == 'us' and now == 'rub':
        konvertirovano = int(symma) * izRUBvUSD
        konvertaciya[user_id + 'symma'] = konvertirovano
        okryglenie(call)
        KonvertV_USD(call)
        messkonvert(call)
    if vochtoperevesti == 'rub' and now == 'us':
        konvertirovano = int(symma) * USD
        konvertaciya[user_id + 'symma'] = konvertirovano
        okryglenie(call)
        KonvertV_RUB(call)
        messkonvert(call)
    if vochtoperevesti == 'eu' and now == 'rub':
        konvertirovano = int(symma) * izRUBvEUR
        konvertaciya[user_id + 'symma'] = konvertirovano
        okryglenie(call)
        KonvertV_EUR(call)
        messkonvert(call)
    if vochtoperevesti == 'rub' and now == 'eu':
        konvertirovano = int(symma) * EUR
        konvertaciya[user_id + 'symma'] = konvertirovano
        okryglenie(call)
        KonvertV_RUB(call)
        messkonvert(call)
    if vochtoperevesti == 'eu' and now == 'us':
        konvertirovano = int(symma) * izUSDvEUR
        konvertaciya[user_id + 'symma'] = konvertirovano
        okryglenie(call)
        KonvertV_EUR(call)
        messkonvert(call)
    if vochtoperevesti == 'us' and now == 'eu':
        konvertirovano = int(symma) * izEURvUSD
        konvertaciya[user_id + 'symma'] = konvertirovano
        okryglenie(call)
        KonvertV_USD(call)
        messkonvert(call)
    json.dump(data,
              open('db/data.json', 'w', encoding='utf-8'),
              indent=2,
              ensure_ascii=False,
              )


def KonvertV_USD(call):  # функция отправки сообщения при переводе в доллары
    user_id = str(call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Ваши траты в долларах = ' + str(konvertaciya[user_id + 'symma']))
    vochtoperevesti = 'В долларах'
    konvertaciya[user_id] = vochtoperevesti


def KonvertV_CNY(call):  # функция отправки сообщения при переводе в юани
    user_id = str(call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Ваши траты в юанях = ' + str(konvertaciya[user_id + 'symma']))
    vochtoperevesti = 'В юанях'
    konvertaciya[user_id] = vochtoperevesti


def KonvertV_RUB(call):  # функция отправки сообщения при переводе в рубли
    user_id = str(call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Ваши траты в рублях = ' + str(konvertaciya[user_id + 'symma']))
    vochtoperevesti = 'В рублях'
    konvertaciya[user_id] = vochtoperevesti


def KonvertV_EUR(call):  # функция отправки сообщения при переводе в евро
    user_id = str(call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Ваши траты в евро = ' + str(konvertaciya[user_id + 'symma']))
    vochtoperevesti = 'В евро'
    konvertaciya[user_id] = vochtoperevesti


def okryglenie(call):  # Функция округления
    user_id = str(call.from_user.id)
    konvertirovano = konvertaciya[user_id + 'symma']
    konvertirovano = round(konvertirovano, 2)
    konvertaciya[user_id + 'symma'] = konvertirovano


def messkonvert(call):  # функция отправки сообщения, о возможности узнать конвертированную трату :)
    user_id = call.message.chat.id
    markup1 = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Траты')
    btn2 = types.KeyboardButton('квт')
    btn3 = types.KeyboardButton('Рассчитать')
    btn4 = types.KeyboardButton('конвертировать')
    markup1.row(btn1, btn2, btn3, btn4)
    bot.send_message(user_id, 'В любой момент вы можете узнать конвертированную трату написав комманду'
                              '"квт"', reply_markup=markup1)


if __name__ == '__main__':
    bot.polling()
    print('Бот остановился! Самое время для загрузки данных')
