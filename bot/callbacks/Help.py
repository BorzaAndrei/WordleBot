from telegram import Update
from telegram.ext import CallbackContext


def help_command(update: Update, context: CallbackContext):
    help_message = """
    This bot helps you keep track of your worlde scores.

    Basic Commands:
    /start - See some basic info about the bot
    /help - See this message

    Point Commands:
    /set_points <first name> <points> <normal or ro> - Set the total number of points for a player in a game mode
    /show_points <normal or ro> - See the total number of points for a game mode
    /calculate <day> - Calculate the winners for a specific day and add them to the total score

    To submit your score for a day, just send your message you get when you complete your wordle!
    """
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_message)
