# -*- coding: utf-8 -*-
"""
    json validation forms
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import Required, Email, AnyOf, Length


# Account Forms:
class RegistrationForm(Form):
    email = StringField('email', [Required(), Email()])
    username = StringField('username', [Required()])
    passwd = PasswordField('passwd', [Required(), Length(min=6, max=25)])


class SocialRegistrationForm(Form):
    provider = StringField('provider', [Required(),
                                        AnyOf('FACEBOOK', 'GOOGLE', 'GITHUB')])
    provider_token = StringField('provider_ident', [Required()])


class LoginForm(Form):
    email = StringField('email', [Required(), Email()])
    passwd = PasswordField('passwd', [Required(), Length(min=6, max=25)])


# Bot Forms:
class CreateBotForm(Form):
    name = StringField('name', [Required(), Length(min=2, max=256)])
    description = StringField('description',
                              [Required(), Length(min=0, max=512)])
