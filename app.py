import sys
import os
import time

from io import BytesIO

import telegram
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler)

from flask import Flask, request, send_file
from fsm import TocMachine

API_TOKEN = '289340714:AAEJ-l9JijFO3y4YYG9br6S2KaL2gCCa4H0'
WEBHOOK_URL = 'https://3e153ebe.ngrok.io/hook'

app = Flask(__name__)
bot = telegram.Bot(token=API_TOKEN)
updater = Updater(API_TOKEN)
dispatcher = updater.dispatcher

machine = TocMachine(
    states=[
        'start',
        'startMessage',

        'local',
        'localWeather',
        'localHumidity',
        'localRain',
        'localWeatherMore',
        'localHumidityMore',
        'localRainMore',      

        'abroad',
        'asia',
        'usa',
        'china',
        'europe',
        'asiaMore',
        'usaMore',
        'chinaMore',
        'europeMore',

        'location',
        'getLocation',

        'others',
        'earthquake',
        'astronomy',
        'knowledge',
        'earthquakeMore',
        'astronomyMore',

        'back'
    ],
    transitions=[
        {
            'trigger': 'advance',
            'source': 'start',
            'dest': 'startMessage',
            'conditions': 'print_start_message'
        },
        {
            'trigger': 'advance',
            'source': 'startMessage',
            'dest': 'local',
            'conditions': 'search_local'
        },
        {
            'trigger': 'advance',
            'source': 'local',
            'dest': 'localWeather',
            'conditions': 'search_local_weather'
        },
        {
            'trigger': 'advance',
            'source': 'local',
            'dest': 'localHumidity',
            'conditions': 'search_local_humidity'
        },
        {
            'trigger': 'advance',
            'source': 'local',
            'dest': 'localRain',
            'conditions': 'search_local_rain'
        },
        {
            'trigger': 'advance',
            'source': 'localWeather',
            'dest': 'localWeatherMore',
            'conditions': 'more_weather'
        },
        {
            'trigger': 'advance',
            'source': 'localHumidity',
            'dest': 'localHumidityMore',
            'conditions': 'more_humidity'
        },
        {
            'trigger': 'advance',
            'source': 'localRain',
            'dest': 'localRainMore',
            'conditions': 'more_rain'
        },
        {
            'trigger': 'advance',
            'source': [
                'localWeather',
                'localHumidity',
                'localRain'
            ],
            'dest': 'local',
            'conditions': 'go_back_1'
        },
        {
            'trigger': 'go_back',
            'source': [
                'localWeatherMore',
                'localHumidityMore',
                'localRainMore'
            ],
            'dest': 'local'
        },
        {
            'trigger': 'advance',
            'source': 'startMessage',
            'dest': 'abroad',
            'conditions': 'search_abroad'
        },
        {
            'trigger': 'advance',
            'source': 'abroad',
            'dest': 'asia',
            'conditions': 'search_asia'
        },
        {
            'trigger': 'advance',
            'source': 'abroad',
            'dest': 'usa',
            'conditions': 'search_usa'
        },
        {
            'trigger': 'advance',
            'source': 'abroad',
            'dest': 'europe',
            'conditions': 'search_europe'
        },
        {
            'trigger': 'advance',
            'source': 'abroad',
            'dest': 'china',
            'conditions': 'search_china'
        },
        {
            'trigger': 'advance',
            'source': 'asia',
            'dest': 'asiaMore',
            'conditions': 'more_asia'
        },
        {
            'trigger': 'advance',
            'source': 'usa',
            'dest': 'usaMore',
            'conditions': 'more_usa'
        },
        {
            'trigger': 'advance',
            'source': 'europe',
            'dest': 'europeMore',
            'conditions': 'more_europe'
        },
        {
            'trigger': 'advance',
            'source': 'china',
            'dest': 'chinaMore',
            'conditions': 'more_china'
        },
        {
            'trigger': 'go_back',
            'source': [
                'usaMore',
                'asiaMore',
                'europeMore',
                'chinaMore'
            ],
            'dest': 'abroad'
        },
        {
            'trigger': 'advance',
            'source': [
                'asia',
                'europe',
                'usa',
                'china'
            ],
            'dest': 'abroad',
            'conditions': 'go_back_1'
        },
        {
            'trigger': 'advance',
            'source': 'startMessage',
            'dest': 'location',
            'conditions': 'search_location'
        },
        {
            'trigger': 'advance',
            'source': 'location',
            'dest': 'getLocation',
            'conditions': 'is_getting_location'
        },
        {
            'trigger': 'advance',
            'source': 'startMessage',
            'dest': 'others',
            'conditions': 'search_others'
        },
        {
            'trigger': 'advance',
            'source': 'others',
            'dest': 'earthquake',
            'conditions': 'search_earthquake'
        },
        {
            'trigger': 'advance',
            'source': 'earthquake',
            'dest': 'earthquakeMore',
            'conditions': 'more_earthquake'
        },
        {
            'trigger': 'advance',
            'source': 'others',
            'dest': 'astronomy',
            'conditions': 'search_astronomy'
        },
        {
            'trigger': 'advance',
            'source': 'astronomy',
            'dest': 'astronomyMore',
            'conditions': 'more_astronomy'
        },
        {
            'trigger': 'advance',
            'source': 'others',
            'dest': 'knowledge',
            'conditions': 'search_knowledge'
        },
        {
            'trigger': 'advance',
            'source': 'others',
            'dest': 'startMessage',
            'conditions': 'go_back_2'
        },
        {
            'trigger': 'advance',
            'source': [
                'earthquake',
                'astronomy'
            ],
            'dest': 'others',
            'conditions': 'go_back_3'
        },
        {
            'trigger': 'advance',
            'source': [
                'local',
                'abroad'
            ],
            'dest': 'back',
            'conditions': 'back_search'
        },
        {
            'trigger': 'go_back',
            'source': [
                'back',
                'abroad',
                'getLocation'
            ],
            'dest': 'startMessage'
        },
        {
            'trigger': 'go_back',
            'source': [
                'earthquakeMore',
                'astronomyMore',
                'knowledge'
            ],
            'dest': 'others'
        }
    ],
    initial='start',
    title='FSM',
    auto_transitions=False,
    show_conditions=True,
    show_auto_transitions=True
)

def _set_webhook():
    status = bot.set_webhook(WEBHOOK_URL)
    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))

def button(bot, update):
    query = update.callback_query

    if query.data == '1':
        machine.abroad_branch = 1
    elif query.data == '2':
        machine.abroad_branch = 2
    elif query.data == '3':
        machine.abroad_branch = 3
    elif query.data == '4':
        machine.abroad_branch = 4
    elif query.data == '5':
        machine.abroad_branch = 5
    elif query.data == '6':
        machine.abroad_branch = 6
    elif query.data == '7':
        machine.abroad_branch = 7

dispatcher.add_handler(CallbackQueryHandler(button))

@app.route('/hook', methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    machine.advance(update)
    return 'ok'

@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io = BytesIO()
    machine.get_graph().draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='fsm.png', mimetype='image/png')

if __name__ == "__main__":
    _set_webhook()
    app.run()