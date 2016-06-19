# -*- coding: utf-8 -*-
"""
    json validation forms
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import Required, Email, AnyOf, Length
from bb8.backend.database import FeedEnum, OAuthProviderEnum


# Account Forms:
class RegistrationForm(Form):
    email = StringField('email', [Required(), Email()])
    username = StringField('username', [Required()])
    passwd = PasswordField('passwd', [Required(), Length(min=6, max=25)])


class SocialRegistrationForm(Form):
    provider = StringField('provider',
                           [Required(),
                            AnyOf([OAuthProviderEnum.Facebook.value,
                                   OAuthProviderEnum.Google.value,
                                   OAuthProviderEnum.Github.value])])
    provider_token = StringField('provider_ident', [Required()])


class LoginForm(Form):
    email = StringField('email', [Required(), Email()])
    passwd = PasswordField('passwd', [Required(), Length(min=6, max=25)])


# Bot Forms:
class CreateBotForm(Form):
    name = StringField('name', [Required(), Length(min=2, max=256)])
    description = StringField('description',
                              [Required(), Length(min=0, max=512)])


# Content Forms
class CreateFeedForm(Form):
    url = StringField('url', [Required()])
    type = StringField('type', [Required(),
                                AnyOf([FeedEnum.RSS.value,
                                       FeedEnum.ATOM.value,
                                       FeedEnum.CSV.value,
                                       FeedEnum.JSON.value,
                                       FeedEnum.XML.value])])
    title = StringField('title', [Required()])
    image_url = StringField('image_url', [Required()])
