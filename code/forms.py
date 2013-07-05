# -*- coding: utf-8 -*-
from wtforms.fields import TextField, BooleanField, PasswordField
from wtforms import Form, validators

from wtforms.validators import (Required, ValidationError, Email, Length)

from wtforms.widgets.core import HiddenInput
from wtforms.ext.sqlalchemy.fields import QuerySelectField


class LoginForm(Form):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    remember = BooleanField('Remember me', default=False)


class RegisterForm(Form):
    first_name = TextField(
        label='Nombre',
        validators=[Required(), Length(2, 40)]
    )

    dni = TextField(
        label='DNI',
        validators=[Required(), Length(7, 8)]
    )

    last_name = TextField(
        label='Apellido',
        validators=[Required(), Length(2, 40)]
    )

    phone = TextField('Telefono',
                      validators=[validators.Length(min=7, max=9)])

    email = TextField(
        label='E-mail',
        validators=[
            Required(),
            Email(),
            Length(
                max=50,
            )
        ]
    )

    cod_dpto = QuerySelectField(get_label='Departamento')
    email_exists = BooleanField(widget=HiddenInput())
    dni_exists = BooleanField(widget=HiddenInput())

    def validate_email_exists(self, field):
        if field.data:
            raise ValidationError()
