import logging
import os

from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.utils.request import Request

from callbacks.Filters import WordleMessageFilter
from callbacks.Help import help_command
from callbacks.Score import Score
from callbacks.Start import start

request = Request(con_pool_size=8)
bot = Bot(token=os.environ['BOT_TOKEN'], request=request)
updater = Updater(bot=bot, use_context=True)
dispatcher = updater.dispatcher
score = Score()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start_up():
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    filter_wordle_message = WordleMessageFilter()
    wordle_input_handler = MessageHandler(filter_wordle_message, score.store_worlde_score)
    dispatcher.add_handler(wordle_input_handler)

    set_points_handler = CommandHandler('set_points', score.set_user_points)
    dispatcher.add_handler(set_points_handler)

    show_points_handler = CommandHandler('show_points', score.print_total_scores)
    dispatcher.add_handler(show_points_handler)

    calculate_points_handler = CommandHandler('calculate', score.calculate_command)
    dispatcher.add_handler(calculate_points_handler)

    help_handler = CommandHandler('help', help_command)
    dispatcher.add_handler(help_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    start_up()
