from telegram import Update
from telegram.ext import CallbackContext


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"I'm the Wordle Score Keeper!\nSend your wordle result and I'll handle the rest!")
