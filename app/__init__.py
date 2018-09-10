from flask import Flask, request
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = _l('Please log in to access this page.')
mail = Mail(app)
boostrap = Bootstrap(app)
moment = Moment(app)
babel = Babel(app)

# creates a SMTPHandler instance, sets its level so that it only reports errors and not warnings, 
# informational or debugging messages, and finally attaches it to the app.logger object from Flask
if not app.debug: # Only send email if app.debug is not true (while not running debugging)
    ###############################
    # this email log thing doesn't work. I'm pretty sure it would if I changed my settings on gmail, but I don't want to
    # these next lines maintain a log file, which will do.
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10) # rotates files. makes sure they don't get too big
    # format class that provides custom formatting
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)# lowering the logging level to the INFO category, both in the application logger and the file logger handler.
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')

    if app.config['MAIL_SERVER']: # Also only when an email server exists
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']: 
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog buggy',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])# 'request' object attribute called 'accept_languages' provides a high-lvl interface 
    # to work with Accept-Language header that clients send with a request. The header specifies client language and locale prefs. defualt usually imported from os
    # best_match() provides to logic to go decide which supported language to display.

from app import routes, models, errors


