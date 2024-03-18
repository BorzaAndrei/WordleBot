import re

from telegram.ext import MessageFilter


class WordleMessageFilter(MessageFilter):
    def filter(self, message):
        if message.text is not None:
            result = re.search("Wordle([-RO]*) ([.,0-9]+) [🎉 ]*([0-9X])/[0-9]", message.text)
            return result is not None
        return False
