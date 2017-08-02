#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic inline bot example. Applies different text transformations.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from uuid import uuid4

import re
import configparser

from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging

import wikiquote
HEADERS = {'User-Agent':'Mozilla/5.0'}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hi! I am an inline bot, you should type my username and a search query.')

def help(bot, update):
    update.message.reply_text('Help!')

def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)

def inlinequery(bot, update):
    query = update.inline_query.query
    if query != "":

        author = wikiquote.search(query)[0]
        try:
            quotes = wikiquote.quotes(author,max_quotes=15)
            results = list()

            logging.debug(author)
            for quote in quotes:
                results.append(
                        InlineQueryResultArticle(id=uuid4(),
                                        title=author,
                                        description=quote,
                                        input_message_content=InputTextMessageContent(
                                            '*{}:*\n{}'.format(author,quote),
                                            parse_mode=ParseMode.MARKDOWN
                                            )
                                        ))
        except wikiquote.utils.DisambiguationPageException:
            results = [InlineQueryResultArticle(id=uuid4(),
                                        title=author+' gives disambiguation',
                                        description='Sorry!',
                                        input_message_content=InputTextMessageContent(
                                            author+' gives a disambiguation page :('
                                        )
                                        )
                    ]

        bot.answer_inline_query(update.inline_query.id, results)
    #update.(results)

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    bot_token = config['config']['token']
    # Create the Updater and pass it your bot's token.
    updater = Updater(bot_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
