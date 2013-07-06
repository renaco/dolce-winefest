# -*- coding: utf-8 -*-
from wtforms.fields import TextField, BooleanField, PasswordField
from wtforms import Form

from wtforms.validators import (Required, ValidationError, Email, Length, Optional)

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

    comment = TextField(
        label='Comment',
        validators=[Optional(), Length(1, 140)]
    )

    cod_dpto = QuerySelectField(get_label='Departamento')
    email_exists = BooleanField(widget=HiddenInput())
    dni_exists = BooleanField(widget=HiddenInput())

    def validate_dni_exists(self, field):
        if field.data:
            raise ValidationError()

    def validate_email_exists(self, field):
        if field.data:
            raise ValidationError()
