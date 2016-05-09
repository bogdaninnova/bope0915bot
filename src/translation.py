import src.config
import urllib.request
import psycopg2
from urllib.parse import quote
import xml.etree.ElementTree as ET

conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='191993'")


def get_translation(word, id=None, is_add=False):
    lang = get_language(word)
    url_translate = 'https://translate.yandex.net/api/v1.5/tr/translate?key=' \
                    + src.config.yandexToken + '&text=' + quote(word) + '&lang=' + lang
    result = 'Error'
    f = urllib.request.urlopen(url_translate)
    root = ET.fromstring(f.read().decode('utf-8'))
    for tr in root.iter():
        if tr.tag == 'text':
            result = tr.text
            if is_add and id is not None:
                if result != word:
                    text = word
                    if lang == 'en':
                        text = result
                    add_word(text, id)
    return result


def add_word(word, id, rating=100):
    conn.cursor().execute("INSERT INTO words(user_id, word, rating)"
                          " values(%s, %s, %s) ON CONFLICT (user_id, word) DO NOTHING",
                          (str(id), word, rating))
    conn.commit()
    return


def get_language(word):
    lang = 'en'
    url_detect = 'https://translate.yandex.net/api/v1.5/tr/detect?key=' \
                 + src.config.yandexToken + '&text=' + quote(word)
    f0 = urllib.request.urlopen(url_detect)
    root0 = ET.fromstring(f0.read().decode('utf-8'))
    for tr in root0.iter():
        if tr.tag == 'DetectedLang':
            if tr.get('lang') == 'en':
                lang = 'ru'
    return lang
