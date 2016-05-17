import psycopg2
import src.config
import telebot
from telebot import types
import src.translation
import time


conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='191993'")


def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            next_word = False
            user_word = True
            if m.text.upper() == 'TEST':
                user_word = False
                cur = conn.cursor()
                cur.execute('select word from mylist where userid = %s and rating != 100 ORDER BY RANDOM() LIMIT 1',
                            (m.chat.id,))
                row = cur.fetchone()
                if row is None:
                    bot.send_message(m.chat.id, "You haven't unknown words in your list.")
                else:
                    translation = src.translation.get_translation(row[0])
                    bot.send_message(m.chat.id, "Word " + row[0] + " is " + translation)
            if m.text.upper() == 'HELP':
                user_word = False
                cur = conn.cursor()
                cur.execute('select count(1) from mylist where userid = %s', (m.chat.id,))
                bot.send_message(m.chat.id, 'You have ' + str(cur.fetchone()[0]) + ' words in your list.')
            cur = conn.cursor()
            cur.execute('select current_word from currentwords where userid = %s', (m.chat.id,))
            row = cur.fetchone()
            if row is not None:
                current_word = row[0]
                if m.text.upper() == 'CANCEL':
                    user_word = False
                    markup = types.ReplyKeyboardMarkup()
                    markup.row('TRANSLATE - ' + current_word)
                    markup.row('LEARN', 'SKIP')
                    markup.row('HELP', 'TEST')
                    bot.send_message(m.chat.id, current_word, reply_markup=markup)
                if m.text.upper() == 'LEARN':
                    conn.cursor().execute("INSERT INTO mylist(userid, word, rating) values(%s, %s, %s)",
                                          (m.chat.id, current_word, 0))
                    conn.commit()
                    next_word = True
                    user_word = False
                elif m.text.upper() == 'SKIP':
                    conn.cursor().execute("INSERT INTO mylist(userid, word, rating) values(%s, %s, %s)",
                                          (m.chat.id, current_word, 100))
                    conn.commit()
                    next_word = True
                    user_word = False
                elif m.text.upper()[:12] == 'TRANSLATE - ':
                    user_word = False
                    markup = types.ReplyKeyboardMarkup()
                    markup.row('LEARN', 'SKIP')
                    markup.row('HELP', 'TEST')
                    translation = src.translation.get_translation(m.text[12:])
                    bot.send_message(m.chat.id, m.text[12:] + ' - ' + translation, reply_markup=markup)
            if next_word:
                cur = conn.cursor()
                cur.execute('select word from wordslist where word not in'
                            ' (select word from mylist where userid = %s) LIMIT 1', (m.chat.id,))
                current_word = cur.fetchone()[0]
                markup = types.ReplyKeyboardMarkup()
                markup.row('TRANSLATE - ' + current_word)
                markup.row('LEARN', 'SKIP')
                markup.row('HELP', 'TEST')
                bot.send_message(m.chat.id, current_word, reply_markup=markup)
                conn.cursor().execute("UPDATE currentwords SET current_word = %s WHERE userID = %s",
                                      (current_word, m.chat.id))
                conn.cursor().execute("INSERT INTO currentwords(userid, current_word)"
                                      " values(%s, %s) ON CONFLICT (userid) DO NOTHING", (m.chat.id, current_word))
                conn.commit()

            if user_word:
                cur = conn.cursor()
                cur.execute('select 1 from mylist where userid = %s and upper(word) = %s',
                                      (m.chat.id, m.text.upper()))
                if cur.fetchone() is not None:
                    markup = types.ReplyKeyboardMarkup()
                    markup.row('TRANSLATE - ' + m.text)
                    markup.row('DROP "' + m.text + '"')
                    markup.row('KNOW', "DON'T KNOW")
                    bot.send_message(m.chat.id, 'Word "' + m.text + '" is in your vocabulary', reply_markup=markup)
                else:
                    markup = types.ReplyKeyboardMarkup()
                    markup.row('TRANSLATE - ' + m.text)
                    markup.row('ADD "' + m.text + '"')
                    markup.row('CANCEL')
                    bot.send_message(m.chat.id, 'Do you want to add word "' + m.text + '" to your vocabulary?',
                                     reply_markup=markup)

if __name__ == '__main__':
    bot = telebot.TeleBot(src.config.botToken)
    bot.set_update_listener(listener)
    bot.polling(none_stop=True)
    while True:
        time.sleep(200)
