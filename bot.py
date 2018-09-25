import logging
import config

from telegram import TelegramError
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)

import database as db
from telegram_func import is_in_chat
from github_api import create_issue, ApiException


class CHStates:
    ASKED_TASK = 1
    ASKED_URL = 2
    ASKED_REVIEWS = 3


class ParseTaskActions:
    ASK_URL = 1
    REVOKE = 2

help_msg = ""

# GENERAL FUNCTIONS
def check_access(func):
    def wrapper(bot, update):
        username = update.message.from_user.username
        if not db.has_user(username):
            if not is_in_chat(username):
                update.message.reply_text("Access denied")
                return ConversationHandler.END
            else:
                db.add_user(username)
            return func(bot, update)
    return wrapper


def choose_task(tasks):
    return tasks[0]


def review_to_str(review):
    return "@{} : {}".format(review["reviewee"], review["task"])


def str_to_review(s):
    words = s.split()
    return words[0][1:], words[2]


# HANDLER FUNCTIONS
@check_access
def help(bot, update):
    update.message.reply_text(help_msg)


def unknown(bot, update):
    update.message.reply_text("Command is not recognized")
    update.message.reply_text(help_msg)


def cancel(bot, update):
    help(bot, update)
    return ConversationHandler.END

@check_access
def start(bot, update):
    help(bot, update)

@check_access
def ask_task(bot, update):
    keyboard_items = db.get_all_tasks()
    keyboard_items.append("/cancel")
    update.message.reply_text("Choose task", reply_markup=ReplyKeyboardMarkup([keyboard_items]))
    return CHStates.ASKED_TASK


def parse_task(bot, update, user_data, action=ParseTaskActions.ASK_URL):
    task = update.message.text
    if db.has_task(task):
        if action == ParseTaskActions.ASK_URL:
            return save_task_ask_url(update, user_data)
        elif action == ParseTaskActions.REVOKE:
            return revoke_task(update)
        else:
            raise RuntimeError("Invalid action")
    else:
        update.message.reply_text("Task name is not valid. Please, choose one from the list.")
        return CHStates.ASKED_TASK


def save_task_ask_url(update, user_data):
    username = update.message.from_user.username
    task = update.message.text
    user_data[username] = task
    update.message.reply_text("Enter link to your repo")
    return CHStates.ASKED_URL


def revoke_task(update):
    username = update.message.from_user.username
    task = update.message.text
    db.revoke_task(username, task)
    return ConversationHandler.END


def parse_url(bot, update, user_data):
    username = update.message.from_user.username
    task = user_data[username]
    repo = update.message.text
    db.add_task(username, task, repo)
    return ConversationHandler.END


@check_access
def ask_incoming_reviews(bot, update):
    username = update.message.from_user
    reviews = db.get_users_incoming_reviews(username)
    keyboard_items = list(map(review_to_str, reviews))
    keyboard_items.append("/cancel")
    update.message.reply_text("Choose task", reply_markup=ReplyKeyboardMarkup([keyboard_items]))
    return CHStates.ASKED_REVIEWS


def complete_review(bot, update):
    reviewer = update.message.from_user.username
    try:
        reviewee, task = str_to_review(update.message.text)
        if db.user_has_incoming_review(reviewee, task):
            db.complete_review(reviewee, reviewer, task)
            return ConversationHandler.END
    except Exception:  # todo throw something meaningful
        pass
    update.message.reply_text("You have no such review")
    return CHStates.ASKED_REVIEWS


@check_access
def take_review(bot, update):
    waiting_tasks = db.get_waiting_tasks()
    if not waiting_tasks:
        update.message.reply_text("There are no available reviews now.")
    else:
        review = choose_task(waiting_tasks)
        reviewee = review["user"]
        reviewer = update.message.from_user.username
        task = review["task"]
        repo_url = review["repo_url"]
        your_reviewee_msg = "Your reviewee is @{}".format(reviewee)
        try:
            review_url = create_issue(reviewee, reviewer, task, repo_url)
            update.message.reply_text(
                your_reviewee_msg + "Created an issue to discuss the review at {}".format(review_url)
            )
            db.assign_review(reviewee, reviewer, task, review_url, has_issue=True)
        except ApiException:
            review_url = repo_url
            update.message.reply_text("Find the code at {}".format(review_url))
            db.assign_review(reviewee, reviewer, task, review_url, has_issue=False)


@check_access
def list_reviews(bot, update):
    username = update.message.from_user.username
    outgoing = db.get_users_outgoing_reviews(username)
    outgoing_list = "\n".join(map(review_to_str(outgoing)))
    update.message.reply_text("Outgoing reviews: {}".format(outgoing_list))
    incoming = db.get_users_incoming_reviews(username)
    incoming_list = "\n".join(map(review_to_str(incoming)))
    update.message.reply_text("Incoming reviews: {}".format(incoming_list))


# HANDLERS
add_task_handler = ConversationHandler(
        entry_points=[CommandHandler("add", ask_task)],
        states={
            CHStates.ASKED_TASK: [MessageHandler(Filters.text, parse_task, pass_user_data=True)],
            CHStates.ASKED_URL: [MessageHandler(Filters.text, parse_url, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

revoke_task_handler = ConversationHandler(
        entry_points=[CommandHandler("revoke", ask_task)],
        states={
            CHStates.ASKED_TASK: [
                MessageHandler(Filters.text, lambda *args: parse_task(action=ParseTaskActions.REVOKE, *args))
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
)

complete_review_handler = ConversationHandler(
        entry_points=[CommandHandler("complete", ask_incoming_reviews)],
        states={
            CHStates.ASKED_REVIEWS: [MessageHandler(Filters.text, complete_review)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
)


handlers = [
    CommandHandler("start", start),
    CommandHandler("help", help),
    add_task_handler,
    revoke_task_handler,
    complete_review_handler,
    CommandHandler("take_review", take_review),
    CommandHandler("list", list_reviews),
    MessageHandler(None, unknown),
]


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename="logs",
        filemode='a'
    )

    token = config.token
    updater = Updater(token=token)
    dp = updater.dispatcher
    for handler in handlers:
        dp.add_handler(handler)
    try:
        updater.start_polling()
        updater.idle()
    except Exception as e:
        open("error.log", "a").write(str(e))


if __name__ == '__main__':
    main()
