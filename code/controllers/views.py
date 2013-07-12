import settings

from flask.views import MethodView
from controllers import (RequestHandler,
                         generate_csrf_token,
                         session)
from flask import Response
from models import User


class Home(MethodView, RequestHandler):

    def post(self):

        if 'user_id' in session:
            session.pop('user_id')

        if 'comment' in session:
            session.pop('comment')

        data = {}
        if settings.XSRF_COOKIES:
            data['csrf_token'] = generate_csrf_token('home')
        return self.render_template('home.html', **data)

    def get(self):
        return self.post()


class Terms(MethodView, RequestHandler):

    def get(self):
        return self.render_template('terms.html',
                                    title='Terminos')


class Thanks(MethodView, RequestHandler):

    def get(self):
        return self.render_template('thanks.html',
                                    title='Gracias',)


class Winners(MethodView, RequestHandler):

    def get(self):
        return self.render_template('winners.html',
                                    title='Ganadores')


class Fan(MethodView, RequestHandler):

    def post(self):
        return self.render_template('fan.html',
                                    title='Fan')

    def get(self):
        return self.post()


class NoFan(MethodView, RequestHandler):

    def post(self):
        return self.render_template('no_fan.html',
                                    title='NoFan')

    def get(self):
        return self.post()


class Download(MethodView, RequestHandler):

    def get(self):
        users = User.query.all()
        generate = '%s,%s,%s,%s,%s,%s,%s \n' % (
            'first_name',
            'last_name',
            'dni',
            'email',
            'created_at',
            'department',
            'comment'
        )
        for user in users:
            generate += '%s,%s,%s,%s,%s,%s,%s \n' % (
                user.first_name,
                user.last_name,
                user.dni,
                user.email,
                user.created_at,
                user.department.name,
                user.comment
            )
        return Response(generate, mimetype='text/csv')
