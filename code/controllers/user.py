import settings

from flask.views import MethodView
from flask import request, redirect, url_for

from models import User, Department
from controllers import (RequestHandler,
                         generate_csrf_token, csrf_protect, logger)

from database import db_session
from forms import RegisterForm

logger = logger(__name__)


class Register(MethodView, RequestHandler):

    def get(self):


        return self.render_template('form.html')

        """
        user = self.current_user
        logger.info('user: %s' % user)
        if user:
            if User.query.filter_by(fb_id=user.fb_id, enabled=True).first():
                return redirect(url_for('instructions'))

        data = {'title': 'Formulario',
                'profile': self.current_user,
                'departments': Department.query.all()}
        if settings.XSRF_COOKIES:
            data['csrf_token'] = generate_csrf_token()
        return self.render_template('form.html', **data)
        """

    def post(self):
        if settings.XSRF_COOKIES:
            csrf_protect()
        form = RegisterForm(request.form)
        form.email_exists.data = bool(User.query.filter_by(
            email=form.email.data).count())
        form.dni_exists.data = bool(User.query.filter_by(
            dni=form.dni.data).count())
        form.cod_dpto.query = Department.query.all()

        if form.validate():
            user = self.current_user
            form.populate_obj(user)
            user.cod_dpto = form.cod_dpto.data.id
            user.enabled = True
            db_session.add(user)
            try:
                db_session.commit()
            except Exception as exc:
                logger.error(exc)
                db_session.rollback()
                db_session.remove()
                self.get()
            else:
                db_session.remove()
                return redirect(url_for('instructions'))
        else:
            logger.error(form.errors)
            return self.get()


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
