import psycopg2
import src.config
import telebot
from telebot import types
import src.translation
import time

current_word = ''

conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='191993'")


def listener(messages):
    global current_word
    for m in messages:
        if m.content_type == 'text':
            if m.text.upper() == '/TEST':
                pass
            nextWord = True
            if current_word != '':
                if m.text.upper() == 'LEARN':
                    conn.cursor().execute("INSERT INTO mylist(userid, word, rating)"
                                          " values(%s, %s, %s)",
                                          (m.chat.id, current_word, 0))
                    conn.commit()
                elif m.text.upper() == 'SKIP':
                    conn.cursor().execute("INSERT INTO mylist(userid, word, rating)"
                                          " values(%s, %s, %s)",
                                          (m.chat.id, current_word, 100))
                    conn.commit()
                elif m.text.upper() == 'TRANSLATE':
                    markup = types.ReplyKeyboardMarkup()
                    markup.row('LEARN', 'SKIP')
                    translation = src.translation.get_translation(current_word)
                    bot.send_message(m.chat.id, current_word + ' - ' + translation,
                                     reply_markup=markup)
                    nextWord = False
            if nextWord:
                cur = conn.cursor()
                cur.execute('select word from wordslist where word not in'
                            ' (select word from mylist where userid = %s) LIMIT 1', (m.chat.id,))
                current_word = cur.fetchone()[0]

                markup = types.ReplyKeyboardMarkup()
                markup.row('LEARN', 'TRANSLATE', 'SKIP')
                bot.send_message(m.chat.id, current_word, reply_markup=markup)


if __name__ == '__main__':
    bot = telebot.TeleBot(src.config.botToken)
    bot.set_update_listener(listener)
    bot.polling(none_stop=True)
    while True:
        time.sleep(200)
