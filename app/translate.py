import json
import requests
from flask import current_app
from flask_babel import _


def translate(text, source_language, dest_language):
    if 'MS_TRANSLATOR_KEY' not in current_app.config or not current_app.config['MS_TRANSLATOR_KEY']: #checks if the key is configured. I need to re-enter the key every time. don't know why
        return _('ERROR: the translation service is not configured.')
    #auth = {'yandex-key': app.config['MS_TRANSLATOR_KEY']}
    key = current_app.config['MS_TRANSLATOR_KEY'] #takes key from os
    lang = source_language + "-" + dest_language 
    str = 'https://translate.yandex.net/api/v1.5/tr.json/translate?key={}&text={}&lang={}' .format(key, text, lang)
    r = requests.get(str)
    if r.status_code != 200: #error message if it isn't a successful 200 code
        return _('Error: the translation service failed.')
    result = json.loads(r.content.decode('utf-8-sig')) 
    return result['text'] #return result with 'text' key specified
