import json
import logging
import os
import random
import re

from telegram import Update
from telegram.ext import CallbackContext

from redis import Redis


class Score:

    def __init__(self):
        self.redis = Redis(host=os.environ['REDIS_HOST'], port=int(os.environ['REDIS_PORT']))
        self.bind_port = int(os.environ['REDIS_PORT'])

    def store_worlde_score(self, update: Update, context: CallbackContext):
        message = re.search("Wordle([-RO]*) ([0-9]+) ([0-9X])/[0-9]", update.message.text)
        is_ro = message.group(1) is not None and len(message.group(1)) > 0
        day = message.group(2)
        user_score = message.group(3)
        user_score = user_score if user_score != 'X' else '100'
        user_name = update.message.from_user["last_name"] if update.message.from_user["first_name"] is None else \
            update.message.from_user["first_name"]

        logging.info(f"{user_name} guessed in {user_score} today.")

        data = self.get_scores_data(update.effective_chat.id)

        if day not in data["normal"]:
            data["normal"][day] = {}
        if day not in data["ro"]:
            data["ro"][day] = {}

        game_type = "ro" if is_ro else "normal"
        data[game_type][day][user_name] = int(user_score)
        self.save_data(update.effective_chat.id, data)

        congratulate_message = ""
        if user_score == '100':
            congratulate_message = random.choice([f"Uff... This one was tough, right {user_name}?",
                                                  f"Maybe next time drink you coffee first!",
                                                  f"Ouchie!",
                                                  f"Oopa!",
                                                  f"Hey, cheer up! Tomorrow can't be worse than this!",
                                                  "Look at the bright side... Ahm... Surely there is a bright side "
                                                  "somewhere..."])
        elif user_score == '1':
            congratulate_message = random.choice([f"WOW! HOLE IN ONE FOR {user_name}",
                                                  f"CHEATER ALERT! CHEATER ALERT! CHEATER ALERT!",
                                                  f"WE GOT A GENIUS OVER HERE!"])
        elif user_score == '2':
            congratulate_message = random.choice([f"Nice one, {user_name}!",
                                                  f"You're getting better {user_name}!",
                                                  f"Great job! Maybe mind sharing your starting word?",
                                                  "Hmm... Great job, I guess..."])
        elif user_score == '3' or user_score == '4':
            congratulate_message = random.choice(["Not great, not terrible.",
                                                  "Nice!",
                                                  "Good one!",
                                                  f"I'm proud of you, {user_name}!",
                                                  "Great!"])
        elif user_score == '5' or user_score == '6':
            congratulate_message = random.choice(["Hey, at least you got it!",
                                                  "I am 100% certain you didn't cheat today! Great job!",
                                                  "Bad luck!",
                                                  "Let's see how the others perform, don't give up yet!",
                                                  "It's ok!"])

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=congratulate_message,
                                 reply_to_message_id=update.message.message_id)

    def calculate_top_for_day(self, update: Update, context: CallbackContext):
        args = ' '.join(context.args)
        split_args = args.split(' ')
        if len(split_args) < 1:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid Command! The structure is "
                                                                            "/calculate {day_number} {normal/ro}")
            return

        day = split_args[0]
        game_type = 'normal' if len(split_args) == 1 or 'ro' not in split_args[1] else 'ro'
        data = self.get_scores_data(update.effective_chat.id)
        if day not in data[game_type]:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid day! Please enter a day where "
                                                                            "players submitted their results!")
            return
        scores = set(
            sorted([(data[game_type][day][player], player) for player in data[game_type][day]], key=lambda x: x[0],
                   reverse=True))
        first_prize = set([x for x in scores if x[0] != 100 and x[0] == min(scores, key=lambda x: x[0])[0]])
        second_set = scores - first_prize
        if len(second_set) > 0:
            second_prize = set([x for x in scores if x[0] != 100 and x[0] == min(second_set, key=lambda x: x[0])[0]])
        else:
            second_prize = set()
        third_set = scores - first_prize - second_prize
        if len(third_set) > 0:
            third_prize = set([x for x in scores if x[0] != 100 and x[0] == min(third_set, key=lambda x: x[0])[0]])
        else:
            third_prize = set()
        for result in scores:
            if result[1] not in data['total_scores'][game_type]:
                data['total_scores'][game_type][result[1]] = 0
            if result in first_prize:
                data['total_scores'][game_type][result[1]] += 3
            elif result in second_prize:
                data['total_scores'][game_type][result[1]] += 2
            elif result in third_prize:
                data['total_scores'][game_type][result[1]] += 1
        self.save_data(update.effective_chat.id, data)

        congratulate_message = ""
        congratulate_message += f"Today's winner{'s' if len(first_prize) > 1 else ''}:" \
                                f" {', '.join([x[1] for x in first_prize])}\n"
        congratulate_message += f"Second prize{'s' if len(second_prize) > 1 else ''}:" \
                                f" {', '.join([x[1] for x in second_prize])}\n"
        congratulate_message += f"Third prize{'s' if len(third_prize) > 1 else ''}:" \
                                f" {', '.join([x[1] for x in third_prize])}\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=congratulate_message)

        scores = self.construct_total_scores_string(update.effective_chat.id, game_type)
        context.bot.send_message(chat_id=update.effective_chat.id, text=scores)

    def construct_total_scores_string(self, chat_id, game_type):
        data = self.get_scores_data(chat_id)
        game_type = "normal" if len(game_type) < 1 else game_type
        sorted_points = dict(sorted(data['total_scores'][game_type].items(), key=lambda item: item[1], reverse=True))
        top_row = 'ENG Wordle Top\n' if 'ro' not in game_type else 'RO Wordle Top\n'
        return top_row + "\n".join([f"{x} has {data['total_scores'][game_type][x]} points" for x in sorted_points])

    def print_total_scores(self, update: Update, context: CallbackContext):
        args = ' '.join(context.args)
        split_args = args.split(' ')
        if len(split_args) != 1:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid Command! The structure is "
                                                                            "/show_points {normal/ro}")
            return
        game_type = split_args[0]
        scores = self.construct_total_scores_string(update.effective_chat.id, game_type)
        context.bot.send_message(chat_id=update.effective_chat.id, text=scores)

    def get_scores_data(self, chat_id):
        data = self.redis.get(f"{chat_id}-scores.json")
        if data is None:
            data = json.dumps({
                "total_scores": {
                    "normal": {},
                    "ro": {}
                },
                "normal": {},
                "ro": {}
            })
            self.redis.set(f"{chat_id}-scores.json", data)
        return json.loads(data)

    def save_data(self, chat_id, data):
        self.redis.set(f"{chat_id}-scores.json", json.dumps(data))

    def set_user_points(self, update: Update, context: CallbackContext):
        args = ' '.join(context.args)
        split_args = args.split(' ')
        if len(split_args) != 3:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid Command! The structure is "
                                                                            "/set_points {first_name} {points} {"
                                                                            "normal/ro}")
            return
        name = split_args[0]
        new_score = split_args[1]
        game_type = split_args[2]
        data = self.get_scores_data(update.effective_chat.id)
        data["total-scores"][game_type][name] = new_score

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Successfully set {name}'s score to {new_score}")
