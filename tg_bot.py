import logging

import redis
import telegram
from environs import Env
from functools import partial
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler

logger = logging.getLogger(__name__)

START, SOLUTION = range(2)


def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text(
        text='Привет, я бот для викторин',
        reply_markup=reply_markup,
    )
    return START


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def handle_new_question_request(bot, update, redis_user_history, redis_questions):
    random_question = redis_questions.randomkey()
    update.message.reply_text(random_question)
    redis_user_history.set(update.message['chat']['id'], random_question)
    return SOLUTION


def handle_solution_attempt(bot, update, redis_user_history, redis_questions):
    last_question = redis_user_history.get(update.message['chat']['id'])
    answer = redis_questions.get(last_question)
    if update.message.text.lower() == answer.split('.')[0].strip().lower():
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')
        return START
    else:
        update.message.reply_text('Неправильно… Попробуешь ещё раз?')
        return SOLUTION


def handle_give_up_request(bot, update, redis_user_history, redis_questions):
    last_question = redis_user_history.get(update.message['chat']['id'])
    answer = redis_questions.get(last_question)
    update.message.reply_text('Правильный ответ: {}'.format(answer))
    return handle_new_question_request(bot, update, redis_user_history, redis_questions)


def main():
    env = Env()
    env.read_env()
    redis_host = env.str('REDIS_HOST')
    redis_port = env.str('REDIS_PORT')
    telegram_token = env.str('TELEGRAM_TOKEN')
    redis_questions = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
    redis_user_history = redis.Redis(host=redis_host, port=redis_port, db=1, decode_responses=True)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    updater = Updater(telegram_token)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START: [
                RegexHandler(
                    '^Новый вопрос$',
                    partial(handle_new_question_request,
                            redis_user_history=redis_user_history,
                            redis_questions=redis_questions)
                )
            ],
            SOLUTION: [
                RegexHandler(
                    '^Новый вопрос$',
                    partial(handle_new_question_request,
                            redis_user_history=redis_user_history,
                            redis_questions=redis_questions)
                ),
                RegexHandler(
                    '^Сдаться$',
                    partial(handle_give_up_request,
                            redis_user_history=redis_user_history,
                            redis_questions=redis_questions)
                ),
                MessageHandler(
                    Filters.text,
                    partial(handle_solution_attempt,
                            redis_user_history=redis_user_history,
                            redis_questions=redis_questions)
                ),
            ],
        },
        fallbacks=[]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
