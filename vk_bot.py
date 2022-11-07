import redis
import vk_api as vk
from environs import Env
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id


def handle_new_question_request(event, vk_api, keyboard, redis_user_history, redis_questions):
    random_question = redis_questions.randomkey()
    vk_api.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=random_question
    )
    redis_user_history.set(event.user_id, random_question)


def handle_solution_attempt(event, vk_api, keyboard, redis_user_history, redis_questions):
    last_question = redis_user_history.get(event.user_id)
    if not last_question:
        handle_new_question_request(event, vk_api, keyboard, redis_user_history, redis_questions)
        return
    answer = redis_questions.get(last_question)
    if event.text.lower() == answer.split('.')[0].strip().lower():
        vk_api.messages.send(
            user_id=event.user_id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        )
    else:
        vk_api.messages.send(
            user_id=event.user_id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message='Неправильно… Попробуешь ещё раз?'
        )


def handle_give_up_request(event, vk_api, keyboard, redis_user_history, redis_questions):
    last_question = redis_user_history.get(event.user_id)
    answer = redis_questions.get(last_question)
    vk_api.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message='Правильный ответ: {}'.format(answer)
    )
    handle_new_question_request(event, vk_api, keyboard, redis_user_history, redis_questions)


def main():
    env = Env()
    env.read_env()
    redis_host = env.str('REDIS_HOST')
    redis_port = env.str('REDIS_PORT')
    redis_questions = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
    redis_user_history = redis.Redis(host=redis_host, port=redis_port, db=1, decode_responses=True)
    vk_session = vk.VkApi(token=env.str('VK_TOKEN'))
    vk_api = vk_session.get_api()

    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':
                handle_new_question_request(event, vk_api, keyboard, redis_user_history, redis_questions)
            elif event.text == 'Сдаться':
                handle_give_up_request(event, vk_api, keyboard, redis_user_history, redis_questions)
            else:
                handle_solution_attempt(event, vk_api, keyboard, redis_user_history, redis_questions)


if __name__ == "__main__":
    main()
