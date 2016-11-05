from flask_wtf import Form
from app.models import User
from app.models import Role
from wtforms import StringField
from wtforms import BooleanField
from wtforms import SubmitField
from wtforms import SelectField
from wtforms import TextAreaField
from wtforms.validators import Required
from wtforms.validators import Length
from wtforms.validators import Email
from wtforms.validators import Regexp
from wtforms import ValidationError


class EditProfileForm(Form):
    name = StringField(
        'Real name',
        validators=[
            Length(0, 64)
        ]
    )
    location = StringField(
        'Location',
        validators=[
            Length(0, 64)
        ]
    )
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    email = StringField(
        'Email',
        validators=[
            Required(),
            Length(1, 64),
            Email()
        ]
    )
    username = StringField(
        'Username',
        validators=[
            Required(),
            Length(1, 64),
            Regexp(
                '^[A-Za-z][A-Za-z0-9_.]*$',
                0,
                'Usernames must have only letters, numbers, dots and underscores'
            )
        ]
    )
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kw):
        super(EditProfileAdminForm, self).__init__(*args, **kw)
        self.role.choices = [
            (role.id, role.name)
            for role in Role.query.order_by(Role.name).all()
        ]
        self.user = user

    def validate_email(self, field):
        if (field.data != self.user.email and User.query.filter_by(email=field.data).first()):
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if (field.data != self.user.username and User.query.filter_by(username=field.data).first()):
            raise ValidationError('Username already in use.')
