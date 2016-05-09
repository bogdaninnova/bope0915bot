# -*- coding: utf-8 -*-
import urllib.request

import src.config
import telebot
from telebot import types
import time
import xml.etree.ElementTree as ET

def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            if m.text.upper() == 'КУРС' or m.text.upper() == '/КУРС':
                markup = types.ReplyKeyboardMarkup()
                markup.row('рубль', 'долар', 'євро')
                bot.send_message(m.chat.id, "Оберіть валюту:", reply_markup=markup)
                pass
            f = urllib.request.urlopen(
                'https://privat24.privatbank.ua/p24/accountorder?oper=prp&PUREXML&apicour&country=ua')
            root = ET.fromstring(f.read())
            userText = m.text.replace("/", "").upper()
            for euro in root.iter('exchangerate'):
                if euro.get('ccy_name_ua') is not None:
                    if userText in euro.get('ccy_name_ua').upper():
                        hide = types.ReplyKeyboardHide()
                        bot.send_message(m.chat.id, "Покупка: " +
                                         str(float(euro.get('buy')) / float(euro.get('unit')) / 10000),
                                         reply_markup=hide)

if __name__ == '__main__':
     bot = telebot.TeleBot(src.config.token)
     bot.set_update_listener(listener)
     bot.polling(none_stop = True)
     while True:
         time.sleep(200)
