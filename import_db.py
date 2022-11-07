import os
import redis

from environs import Env


def parse_questions(text):
    questions = {}
    sections = text.split(sep='\n\n\n')

    for section in sections:
        question = ''
        for block in section.split('\n\n'):
            if 'Вопрос ' in block:
                question = ''.join(block.splitlines(keepends=True)[1:])
            if 'Ответ:' in block and question:
                answer = ''.join(block.splitlines(keepends=True)[1:])
                questions[question] = answer
    return questions


def main():
    env = Env()
    env.read_env()
    redis_host = env.str('REDIS_HOST')
    redis_port = env.str('REDIS_PORT')
    questions_folder = env.str('QUESTIONS_FOLDER')

    redis_questions = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)

    questions = {}
    for filename in os.listdir(questions_folder):
        with open(os.path.join(questions_folder, filename), 'r', encoding='koi8-r') as f:
            text = f.read()
            questions.update(parse_questions(text))
    for question, answer in questions.items():
        redis_questions.set(question, answer)


if __name__ == '__main__':
    main()
