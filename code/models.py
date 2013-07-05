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
    return str(hashlib.sha224(password).hexdigest()).strip()


class SystemUser(UserMixin, Base):
    __tablename__ = 'system_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode(100), nullable=False, unique=True)
    _password = db.Column('password', db.Unicode(100), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    last_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.Unicode(50))
    current_login_at = db.Column(db.DateTime)
    current_login_ip = db.Column(db.Unicode(50))

    def _set_password(self, password):
        #self._password = make_hash(password)
        self._password = crypt_password(password)

    def _get_password(self):
        return self._password

    password = synonym('_password', descriptor=property(_get_password,
                                                        _set_password))

    def valid_password(self, password):
        return crypt_password(password) == self.password

    def is_active(self):
        return self.active

    def __repr__(self):
        return '<%s(%r,  %r)>' % (self.__class__.__name__, self.id,
                                  self.username)


class User(Base):

    __tablename__ = "users"
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Unicode(40), nullable=True)
    last_name = db.Column(db.Unicode(40), nullable=True)
    dni = db.Column(db.Unicode(8), nullable=True, index=True)
    phone = db.Column(db.Unicode(9), nullable=True)
    #gender = db.Column(db.Unicode(10), nullable=True)
    email = db.Column(db.Unicode(50), unique=True, index=True, nullable=True)
    fb_id = db.Column(db.Unicode(100), unique=True, index=True, nullable=False)
    fb_first_name = db.Column(db.Unicode(40), nullable=True)
    fb_last_name = db.Column(db.Unicode(40), nullable=True)
    fb_email = db.Column(db.Unicode(50), unique=True, nullable=True)
    fb_gender = db.Column(db.Unicode(10), nullable=True)
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
    created_at = db.Column(db.DateTime, default=datetime.now)
    winner = db.Column(
        db.Boolean,
        nullable=False,
        server_default=db.text("0"),
        default=False
    )
    user_games = relationship('UserGame', backref='users',
                              lazy='dynamic')
    oauth_token = db.Column(db.Unicode(200), nullable=True, index=True)
    last_updated = db.Column(db.DateTime, onupdate=datetime.now)
    cod_dpto = db.Column(db.Integer, fk('departments.id'))
    department = relationship("Department", backref="users")

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)


class Department(Base):

    __tablename__ = "departments"
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50), nullable=False)

    def __unicode__(self):
        return self.name


class Product(Base):

    __tablename__ = "products"
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(200), nullable=False)
    enabled = db.Column(
        db.Boolean,
        nullable=False,
        server_default=db.text("1"),
        default=True
    )
    created_at = db.Column(db.DateTime, default=datetime.now)
    capsules = relationship('ProductCapsule',
                            backref='products')
    tot_capsules = db.Column(db.Integer)

    def __unicode__(self):
        return self.name


class Capsule(Base):

    __tablename__ = "capsules"
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(200), nullable=False)
    enabled = db.Column(db.Boolean,
                        nullable=False,
                        server_default=db.text("1"),
                        default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __unicode__(self):
        return self.name


class UserGame(Base):
    __tablename__ = "user_game"
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, fk('users.id'))
    answers = db.Column(db.Unicode(32), nullable=False)
    results = db.Column(db.Unicode(12), nullable=False)
    attempts = db.Column(db.Integer, default=0)
    winner = db.Column(
        db.Boolean,
        nullable=False,
        server_default=db.text("0"),
        default=False
    )
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = relationship('User')

class UserGameHistory(Base):
    __tablename__ = "user_game_history"
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, fk('users.id'))
    product_id = db.Column(db.Integer, fk('products.id'))
    capsule_id = db.Column(db.Integer, nullable=True)
    gane_id = db.Column(db.Integer, fk('user_game.id'))


class ProductCapsule(Base):
    __tablename__ = "product_capsule"
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    product_id = db.Column(db.Integer, fk('products.id'), primary_key=True)
    capsule_id = db.Column(db.Integer, fk('capsules.id'), primary_key=True)
    order = db.Column(db.Integer, default=0)
    capsule = relationship("Capsule", backref="products_assocs")


if __name__ == "__main__":

    parser = optparse.OptionParser()
    parser.add_option('-c', '--createdb',
                      dest='createdb', action='store_true')
    parser.add_option('-d', '--dropdb',
                      dest='dropdb', action='store_true')
    parser.add_option('-r', '--recreatedb',
                      dest='recreatedb', action='store_true')
    parser.add_option('-i', '--insert_data',
                      dest='insert_data', action='store_true')
    (options, args) = parser.parse_args()

    def initial_data():

        system_user = SystemUser()
        system_user.username = 'admin'
        system_user.password = '123'
        system_user.admin = True
        db_session.add(system_user)

        cap_capuccino = Capsule(id=1, name=u'Capsule capuccino')
        cap_capuccino_milk = Capsule(id=2, name=u'Capsule leche lungo')
        cap_chococino = Capsule(id=3, name=u'Capsule chococino')
        cap_chococino_milk = Capsule(id=4, name=u'Capsule leche chococino')
        cap_expresso = Capsule(id=5, name=u'Capsula de espresso')
        cap_latte_macchiato = Capsule(id=6, name=u'Capsule latter macchiato')
        cap_latte_macchiato_milk = Capsule(id=7,
                                           name=u'Capsule leche latte macchiato')
        cap_latte = Capsule(id=8, name=u'Capsule latte')
        cap_latte_milk = Capsule(id=9, name=u'Capsule leche latte')
        cap_lungo_descafeinado = Capsule(id=10,
                                         name=u'Capsule lungo descafeinado')
        cap_lungo = Capsule(id=11, name=u'Capsula de lungo')
        cap_skynny = Capsule(id=12, name=u'Capsule skyny cappuccino')
        cap_skynny_milk = Capsule(id=13, name=u'Capsule leche skyny cappuccino')

        db_session.add_all([cap_expresso, cap_lungo, cap_capuccino_milk,
                            cap_latte_macchiato, cap_skynny, cap_latte,
                            cap_chococino_milk, cap_chococino,
                            cap_lungo_descafeinado, cap_latte_macchiato_milk,
                            cap_latte_milk, cap_skynny_milk, cap_capuccino]
                            )

        p1 = Product(id=1, name=u'Cappuccino', tot_capsules=2)
        p1.capsules = [
            ProductCapsule(capsule=cap_capuccino_milk, order=1),
            ProductCapsule(capsule=cap_capuccino, order=2),
        ]

        p2 = Product(id=2, name=u'Chococino', tot_capsules=2)
        p2.capsules = [
            ProductCapsule(capsule=cap_chococino_milk, order=1),
            ProductCapsule(capsule=cap_chococino, order=2),
        ]

        p3 = Product(id=3, name=u'Espresso', tot_capsules=1)
        p3.capsules = [
            ProductCapsule(capsule=cap_expresso, order=1),
        ]

        p4 = Product(id=4, name=u'Caramel Latte Macchiato', tot_capsules=2)
        p4.capsules = [
            ProductCapsule(capsule=cap_latte_macchiato_milk, order=1),
            ProductCapsule(capsule=cap_latte_macchiato, order=2),
        ]

        p5 = Product(id=5, name=u'Latte Macchiato', tot_capsules=2)
        p5.capsules = [
            ProductCapsule(capsule=cap_latte_milk, order=1),
            ProductCapsule(capsule=cap_latte, order=2),
        ]

        p6 = Product(id=6, name=u'Lungo Descafeinado', tot_capsules=1)
        p6.capsules = [
            ProductCapsule(capsule=cap_lungo_descafeinado, order=1),
        ]

        p7 = Product(id=7, name=u'Lungo', tot_capsules=1)
        p7.capsules = [
            ProductCapsule(capsule=cap_lungo, order=1),
        ]

        p8 = Product(id=8, name=u'Cappuccino Skinny', tot_capsules=2)
        p8.capsules = [
            ProductCapsule(capsule=cap_skynny_milk, order=1),
            ProductCapsule(capsule=cap_skynny, order=2),
        ]

        db_session.add_all([p1, p2, p3, p4, p5, p6, p7, p8])

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
