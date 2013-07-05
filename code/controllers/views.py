import settings

from flask.views import MethodView
from controllers import (RequestHandler,
                         generate_csrf_token)


class Home(MethodView, RequestHandler):

    def post(self):
        data = {'title': 'Home'}
        if settings.XSRF_COOKIES:
            data['csrf_token'] = generate_csrf_token()
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


class NoFan(MethodView, RequestHandler):

    def post(self):
        return self.render_template('no_fan.html',
                                    title='NoFan')

    def get(self):
        return self.post()
