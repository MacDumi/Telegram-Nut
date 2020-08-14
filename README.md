# Telegram-Nut

A wrapper (a "nut"🌰 if you like) for the <a href="https://github.com/python-telegram-bot/python-telegram-bot">python-telegram-bot</a> library that allows for a faster creation and deployment of new telegram bots.
The bot also creates a UNIX socket and all the messages sent to that socket are forwarded to connected Telegram users.

## Before trying

Before using the **Telegram-nut** make sure to install all the dependencies by running the following command:
    pip install -r requirements

Once all the dependencies are installed you need to register a new bot by talking to the __BotFather__.
Paste the obtained bot ID into the configuration file.

## Usage

To create a bot is as easy as this:

    from nut import Nut
    bot = Nut.from_config('config_file.cfg')

Start the bot:

    bot.start_bot()
    bot.start_bot(blocking=True)

Stop the bot:

    bot.stop_bot()

To send a group message:

    bot.send_group("Message")

## Using the socket

The bot creates a UNIX socket that can be used by other scripts to send messages through the bot to Telegram users.
To try it out, first start the bot and then run the sample.py script:

    python sample.py sample.cfg

Note that to receive messages through telegram you should first connect with the bot in the telegram application and send a "/start" message to the bot. You should receive a greeting message as a reply.

