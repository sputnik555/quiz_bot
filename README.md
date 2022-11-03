## Квиз-бот
Бот предназначен для проведения викторин в мессенджерах Telegram и VK.

### Переменные окружения
Часть настроек проекта берётся из переменных окружения. Чтобы их определить, создайте файл `.env` и
запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.

Доступны следующие переменные:
- `TELEGRAM_TOKEN` — Токен основного Telegram-бота
- `VK_TOKEN` - Токен VK-бота
- `REDIS_HOST` - Адрес сервера Redis, для хранения базы вопросов и отправленных пользователям вопросов.
- `REDIS_PORT` - Порт сервера Redis


### Запуск бота
Python3 должен быть уже установлен (Требуется версия не выше 3.9). 
Затем используйте `pip` (или `pip3`, если есть конфликт с Python2) для установки зависимостей:
```bash
pip install -r requirements.txt
```
Перед запуском бота в базу данных Redis c индексом 0 должны быть
загружены вопросы (ключ) и правильные ответы (значение)

Для запуска скрипта необходимо выполнить в консоли следующие команды:
1. Для запуска Telegram-бота
```bash
python tg_bot.py
```
2. Для запуска VK-бота
```bash
python vk_bot.py
```