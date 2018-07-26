#!/usr/bin/env python3
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters
import json

THEASK = range(1)
houses = {1: 'Старый', 2: 'Де Сад', 3: 'Современный', 4: 'Ямонтово', 5: 'Калифорния'}
houses_voteCount = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
voted = set()
history = {}

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Из раза в раз пытаемся сделать всё красиво и лаконично, но всё еще выходит не очень. Приношу извинения. Предыдущая система выбора дома себя не оправдала и остались недовольные, поэтому у нас второй тур в который выходят. "Калифорния" и "Ямотово" В "Современном" оказался уличный, сборный бассейн без подогрева что нам не подходит, поэтому его отметаем. Двух аутсайдеров так же оставляем за бортом.')


def ask(bot, update):
    chat_type = update.message.chat['type']
    if chat_type != 'private':
        return ConversationHandler.END
    uname = update.message.from_user['username']
    print(voted)
    print(uname)
    if uname in voted:
        update.message.reply_text('Вы уже проголосовали')
        return ConversationHandler.END

    update.message.reply_text('Введи список домов, начиная с самого классного, заканчивая самым паршивым. '
                              'Номера домов: 1 - старый, 2 - Бабушкин Де Сад, 3 - Современный, 4 - Ямонтовов'
                              '5 - Калифорния. Те дома, который ты не рассматриваешь, можешь не писать.'
                              'Пример: Я хочу отдать свои голоса за #1)Калифорнию #2)Современный #3)Ямонтово, '
                              'для этого нужно написать боту:  5 3 4')
    return THEASK


def get_answer(bot, update):
    uname = update.message.from_user['username']
    seq = str(update.message.text).strip().replace('{', '').replace('}', '').replace(']', '').replace('[', '')
    rating = 5
    for e in seq.split(' '):
        houses_voteCount[str(e)] += rating
        rating -= 1
    voted.add(uname)
    history[uname] = seq
    with open('history', 'w') as f:
        f.write(json.dumps(history))

    with open('votes', 'w') as f:
        f.write(json.dumps(houses_voteCount))

    update.message.reply_text('Ваше мнение будет учтено')
    return ConversationHandler.END

def get_rating(bot, update):
    chat_type = update.message.chat['type']
    if chat_type != 'private':
        return ConversationHandler.END
    rating = ''
    for k in houses_voteCount:
        line = houses[int(k)] + ': ' + str(houses_voteCount[k]) + '\n'
        rating += line

    update.message.reply_text(rating)


def get_history(bot, update):
    out = 'History: \n'
    for k in history:
        line = k + ': ' + history[k] + '\n'
        print(k)
        print(line)
        out += line
    update.message.reply_text(out)


def stop(bot, update):
    return ConversationHandler.END


def main():
    with open('token', 'r') as f:
        token_ = f.readline().strip()

    with open('votes', 'r') as f:
        global houses_voteCount
        houses_voteCount = json.loads(str(f.read()))
        print('vote count: ', houses_voteCount)

    with open('history', 'r') as f:
        global history
        history = json.loads(str(f.read()))
        print('history', history)

    updater = Updater(token=token_)
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    start_handler = CommandHandler('start', start)
    vote_handler = ConversationHandler(
        entry_points=[CommandHandler('vote', ask)],
        states={
            THEASK: [MessageHandler(Filters.text, get_answer)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    rating_handler = CommandHandler('rating', get_rating)
    vote_history_handler = CommandHandler('history', get_history)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(vote_handler)
    dispatcher.add_handler(rating_handler)
    dispatcher.add_handler(vote_history_handler)
    updater.start_polling()


if __name__ == '__main__':
    main()
