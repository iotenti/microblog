import json
import requests
from flask_babel import _
from app import app

def translate(text, source_language, dest_language):
    if 'MS_TRANSLATOR_KEY' not in app.config or not app.config['MS_TRANSLATOR_KEY']:
        return _('ERROR: the translation service is not configured.')
    #auth = {'yandex-key': app.config['MS_TRANSLATOR_KEY']}
    key = app.config['MS_TRANSLATOR_KEY']
    lang = source_language + "-" + dest_language
    r = requests.get('https://translate.yandex.net/api/v1.5/tr.json/getLangs?key={}&text={}&lang={}' .format(key, text, lang))
    if r.status_code != 200:
        return _('Error: the translation service failed.')
    return json.loads(r.content.decode('utf-8-sig'))