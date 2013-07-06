import logging
import settings


from flask.views import MethodView
from flask import request, redirect, url_for, session

from models import User, Department
from controllers import (RequestHandler,
                         generate_csrf_token, csrf_protect)

from database import db_session
from forms import RegisterForm


class Register(MethodView, RequestHandler):

    def get(self):

        data = {'departments': Department.query.all()}
        if settings.XSRF_COOKIES:
            data['csrf_token'] = generate_csrf_token('register')

        return self.render_template('form.html', **data)

    def post(self):

        if 'user_id' in session:
            logging.info('have user')
            return redirect(url_for('thanks'))

        if settings.XSRF_COOKIES:
            csrf_protect('register')

        form = RegisterForm(request.form)
        form.email_exists.data = bool(User.query.filter_by(
            email=form.email.data).count())
        form.dni_exists.data = bool(User.query.filter_by(
            dni=form.dni.data).count())
        form.cod_dpto.query = Department.query.all()
        form.comment.data = session.get('comment')

        if form.validate():
            user = User()
            form.populate_obj(user)
            user.cod_dpto = form.cod_dpto.data.id
            user.enabled = True
            db_session.add(user)
            try:
                db_session.commit()
            except Exception as exc:
                logging.error(exc)
                db_session.rollback()
                db_session.remove()
                return redirect(url_for('thanks'))
            else:
                db_session.remove()
                session['user_id'] = str(user.id)
                return redirect(url_for('thanks'))
        else:
            logging.error(form.errors)
            return redirect(url_for('thanks'))


class Validator(MethodView):

    def post(self):
        status_email = bool((User).query.filter_by(
            email=request.form.get('email')).count())

        status_dni = bool((User).query.filter_by(
            dni=request.form.get('dni')).count())

        if status_email and status_dni:
            data = 'dni|email'
        elif status_email and not status_dni:
            data = 'email'
        elif not status_email and status_dni:
            data = 'dni'
        else:
            data = ''
        return data
