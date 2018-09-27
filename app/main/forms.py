from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User

class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])
    #form will submit when user presses enter with focus on the field
    # __init__ constructor function, which provides values for the formdata and csrf_enabled arguments if they are not provided by the caller. 
    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs: #formdata argument determens from where Flask-WTF gets form submissions. default is to use request.form for post reqs
            kwargs['formdata'] = request.args #is is GET req, so get formdata from the query string in URL which is request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False #bypass CSRF validation for this form
        super(SearchForm, self).__init__(*args, **kwargs)

class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

