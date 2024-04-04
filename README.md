# Telegram бот-ассистент

Telegram-бот, который обращается к API сервиса и узнает статус проверки домашнего задания.

__Статусы:__
- взята на проверку
- проверена:
    - принята
    - возвращена на доработку
---
### Бот умеет
1. Раз в 10 минут опрашивать API сервиса и проверяет статус домашнего задания

2. При обновлении статуса анализирует ответ API и отправляет уведомление в Telegram

3. Логирует свою работу и сообщает о важных проблемах сообщением в Telegram
---
### Как запустить

Для запуска проекта локально необходимо создать файл бота через `@BotFather` и файл `.env` в директории проекта с переменными:<br>

__PRACTICUM_TOKEN__ - ваш токен с Практикума<br>
__TELEGRAM_TOKEN__ - токен вашего телеграм бота (запросить у `@BotFather` в разделе API Token)<br>
__TELEGRAM_CHAT_ID__ - ID вашего telegram (можно получить если написать в бот `@userinfobot`)

---
### Деплой бота

Вариант 1. Бот может работать локально на компьютере или на базе Android можно установить Termux, Linux-терминал для Android.

Вариант 2. Загрузить бота на облачный сервис, например `pythonanywhere`.
