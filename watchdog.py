#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This Bot uses the Updater class to handle the bot.
you can config it to watch processes on system
"""

from optparse import OptionParser
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import os
import requests
import json

__author__ = 'sekely'

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

class BotError(Exception):
    pass


class TestCase(object):
    test_types = ['pid', 'rest', 'file', 'custom']

    def __init__(self, test_type, name=None, schedule=1):
        if test_type not in self.test_types:
            raise BotError("illegal test type")
        self.test_type = test_type
        self.name = name
        self.schedule=schedule

    def test(self):
        raise BotError("test not implemented")


class PidTest(TestCase):

    def __init__(self, pid, schedule=1):
        super(PidTest, self).__init__('pid', pid, schedule)
        self.pid = pid

    def test(self):
        """ Check For the existence of a unix pid. """
        try:
            os.kill(self.pid, 0)
        except OSError:
            return 'Not Exist'
        else:
            return 'OK'


class RestTest(TestCase):

    def __init__(self, endpoint, schedule=1, params=None):
        super(RestTest, self).__init__('rest', endpoint, schedule)
        self.endpoint = endpoint
        self.params = params if params else {}

    def test(self):
        r = requests.get(self.endpoint, params=self.params, verify=False)
        resp = json.loads(r.text)
        return resp['status']


class FileTest(TestCase):

    def __init__(self, file_path, schedule=1):
        super(FileTest, self).__init__('rest', file_path, schedule)
        self.path = file_path

    def test(self):
        pass


def test_factory(test_type):
    if test_type == 'pid':
        return PidTest
    if test_type == 'rest':
        return RestTest
    if test_type == 'file':
        return FileTest
    if test_type == 'custom':
        return TestCase
    raise BotError('test type %s not supported' % test_type)


class Watchdog(object):
    test_list = {}

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
        for test_name, test in self.test_list.iteritems():
            bot.sendMessage(update.message.chat_id, text='test %s status: %s' %(test_name, test.test()))

    def watch(self, bot, update):
        command_args = update.message.text.split()[1:]
        test_type = command_args[0]
        args = command_args[1:]
        test_cls = test_factory(test_type)
        test = test_cls(*args)
        self.test_list[test.name] = test
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
