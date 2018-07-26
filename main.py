#!/usr/bin/env python3
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters
import json

THEASK = range(1)
houses = {1: 'Старый', 2: 'Де Сад', 3: 'Современный', 4: 'Ямонтово', 5: 'Калифорния'}
houses_voteCount = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
voted = set()
history = {}

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='123')


def ask(bot, update):
    chat_type = update.message.chat['type']
    if chat_type != 'private':
        return ConversationHandler.END
    uname = update.message.from_user['username']
    if uname in voted:
        update.message.reply_text('Вы уже проголосовали')

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
        houses_voteCount[int(e)] += rating
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
    for k, v in houses_voteCount:
        line = houses[k] + ': ' + str(houses_voteCount[k]) + '\n'
        rating += line

    update.message.reply_text(rating)


def get_history(bot, update):
    history = ''
    for k, v in history:
        line = k + ': ' + v + '\n'
        history += line
    update.message.reply_text(history)


def stop(bot, update):
    return ConversationHandler.END


def main():
    with open('token', 'r') as f:
        token_ = f.readline().strip()
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
    dispatcher.add_handler(rating_handler)
    dispatcher.add_handler(vote_history_handler)
    updater.start_polling()


if __name__ == '__main__':
    main()
