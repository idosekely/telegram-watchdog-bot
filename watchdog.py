#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This Bot uses the Updater class to handle the bot.
you can config it to watch processes on system
"""

from optparse import OptionParser
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from tests import test_list, test_factory
import logging

__author__ = 'sekely'

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.


class Watchdog(object):

    def __init__(self, token):
        # Create the EventHandler and pass it your bot's token.
        self.updater = Updater(token)

        # Get the dispatcher to register handlers
        dp = self.updater.dispatcher

        # on different commands - answer in Telegram
        dp.addHandler(CommandHandler("start", self.start))
        # dp.addHandler(CommandHandler("help", self.help))
        dp.addHandler(CommandHandler("watch", self.watch))
        dp.addHandler(CommandHandler("status", self.status))

        # log all errors
        dp.addErrorHandler(self.error)

    def start_bot(self):
        # Start the Bot
        self.updater.start_polling()

        # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()

    def start(self, bot, update):
        bot.sendMessage(update.message.chat_id, text='Hi!')

    def status(self, bot, update):
        for test_name, test in test_list.iteritems():
            status = test.run()
            bot.sendMessage(update.message.chat_id, text='test %s status: %s' % (test_name, status))

    def watch(self, bot, update):
        command_args = update.message.text.split()[1:]
        test_type = command_args[0]
        args = command_args[1:]
        test_cls = test_factory(test_type)
        test = test_cls(*args)
        test_list[test.name] = test
        bot.sendMessage(update.message.chat_id, text='watching on %s' % (test.name, ))

    def error(self, bot, update, error):
        logger.warn('Update "%s" caused error "%s"' % (update, error))


def get_parser():
    parser = OptionParser()
    parser.add_option('-t', '--token', dest='token', help='bot token')
    return parser.parse_args()


def main():
    print "starting watchdog bot"
    options, _ = get_parser()
    bot = Watchdog(options.token)
    bot.start_bot()

if __name__ == '__main__':
    main()
