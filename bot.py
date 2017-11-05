import re
import os
import subprocess

from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler, Updater

import logging
logging.basicConfig(level=logging.DEBUG)

TG_TOKEN = os.environ['CATULLUS_TOKEN']


def inline_handler(bot, update):
    query = update.inline_query.query

    if query == '':
        return

    try:
        poem = int(query)
        try:
            with open(os.path.join("carmen", "catullus{}.txt".format(poem))) as f:
                content = f.read()
                update.inline_query.answer([
                    InlineQueryResultArticle(
                        id=poem,
                        title="{}: {}".format(poem, content.split('\n')[0]),
                        input_message_content=InputTextMessageContent(content))])
        except FileNotFoundError as e:
            print(e)
    except ValueError:
        try:
            grepout = subprocess.check_output(["grep", "-r", "-i", "-n", query, "carmen"]).decode("utf-8")
        except subprocess.CalledProcessError:
            update.inline_query.answer([])
            return

        answers = []
        grepre = re.compile(r'carmen/catullus(\d+)\.txt:(\d+):(.*)')
        for line in grepout.split('\n'):
            match = grepre.search(line)
            if match:
                answers.append(InlineQueryResultArticle(
                        id="{}:{}".format(match.group(1), match.group(2)),
                        title=match.group(3),
                        input_message_content=InputTextMessageContent(match.group(3))))
                with open(os.path.join("carmen", "catullus{}.txt".format(match.group(1)))) as f:
                    answers.append(InlineQueryResultArticle(
                            id="{}:{}:poem".format(match.group(1), match.group(2)),
                            title="(Whole poem) " + match.group(3),
                            input_message_content=InputTextMessageContent(f.read())))

        update.inline_query.answer(answers[0:50])

if __name__ == "__main__":
    updater = Updater(token=TG_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(InlineQueryHandler(inline_handler))
    updater.start_polling()
