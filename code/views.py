from flask.views import MethodView
from models import UserGame, Product
from controllers import RequestHandler, authenticated
from flask import url_for, request, redirect


class Home(MethodView, RequestHandler):

    def post(self):

        print "zxzx"
        return self.render_template('home.html',
                                    title='Home',
                                    redirect_if_logged=url_for('form'))

    def get(self):

        return self.render_template('home.html')
        #return self.post()


class Terms(MethodView, RequestHandler):

    def get(self):
        return self.render_template('terms.html',
                                    title='Terminos')


def _result(result_id, user_id):
    if not result_id:
        return None

    result = UserGame.query.filter_by(id=result_id,
                                      user_id=user_id).first()
    if not result:
        return None
    return result


class Retry(MethodView, RequestHandler):

    @authenticated
    def get(self):

        results = []
        result_id = request.args.get('result')
        result = _result(result_id, self.current_user.id)

        if not result:
            return redirect(url_for('home'))

        for result in result.results.split():
            pid = result.split(':')[0]
            result_text = int(result.split(':')[1]) and 'good' or 'bad'
            product = Product.query.filter_by(id=pid).first()
            results.append({'product_id':
                            str(pid).zfill(2),
                            'result': result_text,
                            'name': product.name})

        return self.render_template('retry.html',
                                    title='Reintento',
                                    results=results)


class Thanks(MethodView, RequestHandler):

    @authenticated
    def get(self):

        results = []
        result_id = request.args.get('result')
        result = _result(result_id, self.current_user.id)

        if not result:
            return redirect(url_for('home'))

        for result in result.results.split():
            pid = result.split(':')[0]
            product = Product.query.filter_by(id=pid).first()
            results.append({'product_id': str(pid).zfill(2),
                            'name': product.name})

        return self.render_template('thanks.html',
                                    title='Gracias',
                                    results=results)


class Winners(MethodView, RequestHandler):

    def get(self):
        return self.render_template('winners.html',
                                    title='Ganadores')


class Instructions(MethodView, RequestHandler):

    @authenticated
    def get(self):

        return self.render_template('instructions.html',
                                    title='Instrucciones')


class NoFan(MethodView, RequestHandler):

    def post(self):
        return self.render_template('no_fan.html',
                                    title='NoFan')

    def get(self):
        return self.post()


