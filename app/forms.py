from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import StringField, SubmitField, TextAreaField, SelectField, FileField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, Email, EqualTo, ValidationError
from flask_babel import lazy_gettext as _l
from .models import User

class VideoUploadForm(FlaskForm):
    video_file = FileField(_l('Upload Video or Audio'), 
                          validators=[FileRequired(), FileAllowed(['mp4', 'avi', 'mov', 'mkv', 'mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac'], _l('Only video or audio files are allowed!'))],
                          render_kw={"class": "form-control"})
    
    model = SelectField(_l('Whisper Model'),
                       choices=[('tiny', _l('Tiny (fastest)')),
                               ('base', _l('Base')),
                               ('small', _l('Small')),
                               ('medium', _l('Medium')),
                               ('large', _l('Large (most accurate)'))],
                       default='small',
                       render_kw={"class": "form-control"})
    
    src_language = SelectField(_l('Source Language'),
                              choices=[('auto', _l('Auto-detect')),
                                      ('en', _l('English')),
                                      ('zh', _l('Chinese')),
                                      ('ja', _l('Japanese')),
                                      ('ko', _l('Korean')),
                                      ('es', _l('Spanish')),
                                      ('fr', _l('French')),
                                      ('de', _l('German'))],
                              default='auto',
                              render_kw={"class": "form-control"})
    
    dest_language = SelectField(_l('Target Language'),
                               choices=[('en', _l('English')),
                                       ('zh-cn', _l('Chinese (Simplified)')),
                                       ('zh-tw', _l('Chinese (Traditional)')),
                                       ('ja', _l('Japanese')),
                                       ('ko', _l('Korean')),
                                       ('es', _l('Spanish')),
                                       ('fr', _l('French')),
                                       ('de', _l('German'))],
                               default='zh-cn',
                               render_kw={"class": "form-control"})
    
    translation_method = SelectField(_l('Translation Method'),
                                   choices=[('llm', _l('LLM (ChatGPT) - Better Quality')),
                                           ('google', _l('Google Translate - Faster'))],
                                   default='llm',
                                   render_kw={"class": "form-control"})
    
    submit_button = SubmitField(_l('Process Media'), render_kw={"class": "btn btn-primary btn-lg"})

class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired(), Length(min=4, max=20)],
                          render_kw={"class": "form-control", "placeholder": _l("Enter username")})
    password = PasswordField(_l('Password'), validators=[DataRequired()],
                            render_kw={"class": "form-control", "placeholder": _l("Enter password")})
    remember_me = BooleanField(_l('Remember Me'), render_kw={"class": "form-check-input"})
    submit = SubmitField(_l('Sign In'), render_kw={"class": "btn btn-primary btn-block"})

class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired(), Length(min=4, max=20)],
                          render_kw={"class": "form-control", "placeholder": _l("Choose username")})
    email = StringField(_l('Email'), validators=[DataRequired(), Email()],
                       render_kw={"class": "form-control", "placeholder": _l("Enter email")})
    password = PasswordField(_l('Password'), validators=[DataRequired(), Length(min=6)],
                            render_kw={"class": "form-control", "placeholder": _l("Choose password")})
    password2 = PasswordField(_l('Repeat Password'), 
                             validators=[DataRequired(), EqualTo('password', message=_l('Passwords must match'))],
                             render_kw={"class": "form-control", "placeholder": _l("Repeat password")})
    submit = SubmitField(_l('Register'), render_kw={"class": "btn btn-success btn-block"})

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different username.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different email address.'))

class OcrForm(FlaskForm):
    image_file = FileField(_l('Upload Image'), 
                          validators=[FileRequired(), FileAllowed(['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'], _l('Only image files are allowed!'))],
                          render_kw={"class": "form-control"})
    
    extract_urls = BooleanField(_l('Extract URLs'), 
                               default=True,
                               render_kw={"class": "form-check-input"})
    
    submit_button = SubmitField(_l('Extract Text'), render_kw={"class": "btn btn-primary btn-lg"})