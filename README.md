# expenses-conversion-bot
This bot have his own database on redis with permanent state storage. 
And it has all files to deploy it on Heroku. 
Messages in the bot on russian language, but i shure you can google translate it. 

Полный функционал бота:
1.Запись всех дневных трат в базу данных(без возможности указать цель траты, но скоро появится)
На выбор 4 валюты трат:Рубли, Доллары, Евро, Юани

2.Возможна дальнейшая конвертация в одну из вышеуказанных валют, сконвертированое число так же сохраняется в бд, 
вместе с валютой в которую сконвертировали

Особенности:

Пользоваться ботом можно, писав только сумму траты, остальная навигация происходит при помощи reply или inline клавиатур

Техническая информация:
1.База данных преполагается на redis, но если по каким-то причинам бот не подключится к redis, то будет использовать локальная база данных
на json.

2.Все данные перманентно сохраняются на redis и даже если что-то произойдёт и сервер перезапустится, то данные не исчезнут

3.Также есть обработка состояний(функция dispatcher) и все переходы по функциям происходят в основном через неё

4.Имеются 2 утилиты, которые делают ваш код красивее(isort и black)
