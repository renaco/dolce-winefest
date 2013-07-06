# -*- coding: utf-8 -*-
import hashlib
import optparse
import sqlalchemy as db

from sys import exit
from datetime import datetime
from database import Base, init_db, drop_db, db_session
from sqlalchemy.orm import relationship, synonym

from flask.ext.login import UserMixin


def fk(*args, **kwargs):
    kwargs['ondelete'] = 'CASCADE'
    return db.ForeignKey(*args, **kwargs)


def crypt_password(password):
    return str(hashlib.sha224(
        password).hexdigest()).strip()


class SystemUser(UserMixin, Base):

    __tablename__ = "system_users"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.Unicode(100),
        nullable=False,
        unique=True
    )

    _password = db.Column(
        'password',
        db.Unicode(100),
        nullable=False
    )

    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    admin = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    last_login_at = db.Column(
        db.DateTime
    )

    last_login_ip = db.Column(
        db.Unicode(50)
    )

    current_login_at = db.Column(
        db.DateTime
    )

    current_login_ip = db.Column(
        db.Unicode(50)
    )

    def _set_password(self, password):
        self._password = crypt_password(password)

    def _get_password(self):
        return self._password

    password = synonym(
        '_password',
        descriptor=property(
            _get_password,
            _set_password)
    )

    def valid_password(self, password):
        return crypt_password(
            password) == self.password

    def is_active(self):
        return self.active

    def __repr__(self):
        return '<%s(%r,  %r)>' % (
            self.__class__.__name__,
            self.id,
            self.username)


class User(Base):

    __tablename__ = "users"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    first_name = db.Column(
        db.Unicode(40),
        nullable=True
    )

    last_name = db.Column(
        db.Unicode(40),
        nullable=True
    )

    dni = db.Column(
        db.Unicode(8),
        nullable=True,
        index=True,
        unique=True
    )

    email = db.Column(
        db.Unicode(50),
        unique=True,
        index=True,
        nullable=True
    )

    reply_email = db.Column(
        db.Boolean,
        nullable=False,
        server_default=db.text("0"),
        default=False
    )

    enabled = db.Column(
        db.Boolean,
        nullable=False,
        server_default=db.text("0"),
        default=0
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.now
    )

    winner = db.Column(
        db.Boolean,
        nullable=False,
        server_default=db.text("0"),
        default=False
    )

    last_updated = db.Column(
        db.DateTime,
        onupdate=datetime.now
    )

    cod_dpto = db.Column(
        db.Integer,
        fk('departments.id')
    )

    department = relationship(
        "Department",
        backref="users"
    )

    comment = db.Column(
        db.UnicodeText(),
        nullable=True
    )

    def __unicode__(self):
        return '%s %s' % (
            self.first_name,
            self.last_name)


class Department(Base):

    __tablename__ = "departments"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.Unicode(50),
        nullable=False
    )

    def __unicode__(self):
        return self.name


if __name__ == "__main__":

    parser = optparse.OptionParser()
    parser.add_option(
        '-c', '--createdb',
        dest='createdb',
        action='store_true')

    parser.add_option(
        '-d', '--dropdb',
        dest='dropdb',
        action='store_true')

    parser.add_option(
        '-r', '--recreatedb',
        dest='recreatedb',
        action='store_true')

    parser.add_option(
        '-i', '--insert_data',
        dest='insert_data',
        action='store_true')

    (options, args) = parser.parse_args()

    def initial_data():

        system_user = SystemUser()
        system_user.username = 'admin'
        system_user.password = '123'
        system_user.admin = True
        db_session.add(system_user)

        db_session.add_all([
            Department(id="01", name=u"LIMA"),
            Department(id="02", name=u"CALLAO"),
            Department(id="03", name=u"AMAZONAS"),
            Department(id="04", name=u"ANCASH"),
            Department(id="05", name=u"APURIMAC"),
            Department(id="06", name=u"AREQUIPA"),
            Department(id="07", name=u"AYACUCHO"),
            Department(id="08", name=u"CAJAMARCA"),
            Department(id="09", name=u"CUSCO"),
            Department(id="10", name=u"HUANCAVELICA"),
            Department(id="11", name=u"HUANUCO"),
            Department(id="12", name=u"ICA"),
            Department(id="13", name=u"JUNIN"),
            Department(id="14", name=u"LA LIBERTAD"),
            Department(id="15", name=u"LAMBAYEQUE"),
            Department(id="16", name=u"LORETO"),
            Department(id="17", name=u"MADRE DE DIOS"),
            Department(id="18", name=u"MOQUEGUA"),
            Department(id="19", name=u"PASCO"),
            Department(id="20", name=u"PIURA"),
            Department(id="21", name=u"PUNO"),
            Department(id="22", name=u"SAN MARTIN"),
            Department(id="23", name=u"TACNA"),
            Department(id="24", name=u"TUMBES"),
            Department(id="25", name=u"UCAYALI"),
        ])

        db_session.commit()
        exit(0)

    if options.dropdb:
        drop_db()
        exit(0)

    if options.createdb:
        init_db()
        exit(0)

    if options.recreatedb:
        drop_db()
        init_db()
        initial_data()

    if options.insert_data:
        initial_data()
