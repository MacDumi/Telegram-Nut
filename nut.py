#!/usr/bin/env python3
import pandas as pd
import numpy as np
import time, sys, os
import threading
import logging
import socket
import json
from configparser import ConfigParser
from telegram.ext import Updater, CommandHandler, MessageHandler

class Nut:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'Nut_bot')
        # Enable logging

        logging.basicConfig(filename=f'{self.name}.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=kwargs.get('log_level', logging.INFO))
        logger = logging.getLogger(self.name)
        self._socket_name = f"/tmp/{self.name}"
        bot_id = kwargs.get('id', None)
        if not bot_id:
            logger.error('No bot ID was provided')
            return
        self.updater = Updater(bot_id, use_context=True)
        self.connected = kwargs.get('connected', [])
        self._start_msg = kwargs.get('start_msg', f'Hi! Thanks for starting {self.name}')
        self._stop_msg = kwargs.get('stop_msg', f'Sorry to see you leave')
        self._help_msg = kwargs.get('help_msg', f'This is supposed to help')

        # Get the dispatcher to register handlers
        self._dp = self.updater.dispatcher

    @classmethod
    def from_config(cls, path, **kwargs):
        config = ConfigParser()
        if not config.read(path):
            logging.error(f'Could not read the config file at: {path}')
            return
        if not config.has_section('BOT'):
            logging.error('The config file does not contain a BOT section')
            return
        conf = dict(config['BOT'])
        if config.has_section('CONNECTED'):
            conf['connected'] = json.loads(config['CONNECTED']['connected'])
        return cls(**conf)

    @property
    def start_msg(self, message):
        if type(message) == str:
            self._start_msg = message
        else:
            print('Only string messages are allowed')

    @property
    def stop_msg(self, message):
        if type(message) == str:
            self._stop_msg = message
        else:
            print('Only string messages are allowed')

    @property
    def help_msg(self, message):
        if type(message) == str:
            self._help_msg = message
        else:
            print('Only string messages are allowed')

    def start(self, update, context):
        id_ = update.message.chat_id
        if id_ not in self.connected:
            self.connected.append(id_)
            logging.info(f'User with ID: {id_} connected')
        update.message.reply_text(self._start_msg)

    def stop(self, update, context):
        id_ = update.message.chat_id
        if id_ in self.connected:
            self.connected.remove(id_)
            update.message.reply_text(self._stop_msg)
            logging.info(f'User with ID: {id_} disconnected')

    def help(self, update, context):
        update.message.reply_text(self._help_msg)


    def listen(self, server):
        while True:
            datagram = server.recv(1024).decode(encoding='UTF-8')
            if datagram:
                logging.info(f'Message received: {datagram}')
                self.send_group(datagram)

    def send_group(self, message):
        try:
            for id_ in self.connected:
                self.updater.bot.send_message(id_, message)
        except Exception as e:
            logging.error(f'Something is wrong: {e}')

    def add_basic_handlers(self):
        # on different commands - answer in Telegram
        # custom methods should be added separately
        self._dp.add_handler(CommandHandler("start", self.start))
        self._dp.add_handler(CommandHandler("stop",  self.stop))
        self._dp.add_handler(CommandHandler("help",  self.help))

    def start_bot(self, blocking=False):
        # Create the socket
        if os.path.exists(self._socket_name):
            os.remove(self._socket_name)

        self._server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self._server.bind(self._socket_name)
        logging.debug("Created the socket")
        # Make a listening thread and start it
        self._listener = threading.Thread(target = self.listen, args=(self._server,))
        self._listener.setDaemon(True)
        self._listener.start()
        logging.debug("Started the listening thread")

        # Add some handlers
        self.add_basic_handlers()

        # Start the Bot
        self.updater.start_polling()
        logging.info(f'{self.name} started')

        # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
        # SIGABRT. This should be used most of the time, since start_polling() is
        # non-blocking and will stop the bot gracefully.
        if blocking:
            self.updater.idle()

    def stop_bot(self):
        # Stop the bot
        self.updater.stop()
        logging.info(f'{self.name} was stopped')
