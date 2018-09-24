import logging
from telegram import TelegramError
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)

import db

class CHStates:
    ASKED_TASK = 1
    ASKED_URL = 2


# FUNCTIONS
def check_access(update):
    users = db.get_all_logins()
    if update.message.from_user.username not in users:
        return False
    return True


def deny_access(update):
    update.message.reply_text("Access denied")


def check_chat_presence(update):
    pass

help_msg = ""


def choose_task(tasks):
    return tasks[0]


def create_issue():
    pass

# HANDLER FUNCTIONS
def help(bot, update):
    if not check_access(update):
        deny_access(update)
    update.message.reply_text(help_msg)


def unknown(bot, update):
    if not check_access(update):
        deny_access(update)
    update.message.reply_text("Command is not recognized")
    update.message.reply_text(help_msg)


def cancel(bot, update):
    help(bot, update)
    return ConversationHandler.END


def start(bot, update):
    if not check_access(update):
        if check_chat_presence(update):
            db.add_user(update.message.from_user.username)
        else:
            deny_access(update)
    update.message.reply_text(help_msg)


def ask_task(bot, update):
    if not check_access(update):
        deny_access(update)
    keyboard_items = db.get_all_tasks()
    keyboard_items.append("/cancel")
    update.message.reply_text("Choose task", reply_markup=ReplyKeyboardMarkup([keyboard_items]))
    return CHStates.ASKED_TASK


def parse_task(bot, update):
    if update.message.text in db.get_all_tasks():
        save()
        return ConversationHandler.END
    else:
        update.message.reply_text("Task name is not valid. Please, choose one from the list.")
        return CHStates.ASKED_TASK


def parse_task_ask_url(bot, update):
    if update.message.text in db.get_all_tasks():
        save()
        update.message.reply_text("Enter link to your repo")
        return CHStates.ASKED_URL
    else:
        update.message.reply_text("Task name is not valid. Please, choose one from the list.")
        return CHStates.ASKED_TASK


def parse_url(bot, update):
    if True:
        save()
        return ConversationHandler.END
    else:
        update.message.reply_text("Repo link is not valid. Please, enter another one.")
        return CHStates.ASKED_URL


def take_review(bot, update):
    if not check_access(update):
        deny_access(update)
    waiting_tasks = db.get_waiting_tasks()
    if not waiting_tasks:
        update.message.reply_text("There are no available reviews now.")
    else:
        task = choose_task(waiting_tasks)
        create_issue()
        db.add_review(reviewer=update.message.from_user.username, reviewee=task["user"], task)
        update.message.reply_text("")


def list_reviews(bot, update):
    if not check_access(update):
        deny_access(update)
    mine = db.get_user_tasks(update.message.from_user.username)
    # todo make response
    update.message.reply_text("\n".join(mine))
    theirs = db.get_user_reviews(update.message.from_user.username)
    update.message.reply_text("\n".join(theirs))


add_task_handler = ConversationHandler(
        entry_points=[CommandHandler("add_task", ask_task)],
        states={
            CHStates.ASKED_TASK: [MessageHandler(Filters.text, parse_task_ask_url)],
            CHStates.ASKED_URL: [MessageHandler(Filters.text, parse_url)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

close_task_handler = ConversationHandler(
        entry_points=[CommandHandler("close_task", ask_task)],
        states={
            CHStates.ASKED_TASK: [MessageHandler(Filters.text, parse_task)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
)


handlers = [
    CommandHandler("start", start),
    CommandHandler("help", help),
    add_task_handler,
    close_task_handler,
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

    token = open("token", "r").read().strip()
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
