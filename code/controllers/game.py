import settings

from random import shuffle
from models import UserGame, Product, Capsule
from database import db_session

from flask import url_for, redirect
from flask.views import MethodView, request

from controllers import (RequestHandler, logger,
                         generate_csrf_token, csrf_protect, authenticated)
from urllib import unquote
from sqlalchemy.sql import func

logger = logger(__name__)


def set_format_data(data):
    questions = []
    if data:
        data = unquote(data)
        parts = data.split(',')
        if len(parts) == 3:
            for x in parts:
                if ':' not in x:
                    break
                data = x.split(':')
                if not data[0].isdigit():
                    break
                pid = int(data[0])
                choices = data[1]
                if '-' in choices:
                    choices = [int(x) for x in choices.split('-')]
                else:
                    if choices:
                        choices = [int(choices)]
                    else:
                        choices = []
                questions.append({'pid': pid, 'choices': choices})
    return questions if len(questions) == 3 else None


class Game(MethodView, RequestHandler):

    @authenticated
    def get(self):

        questions = []
        limit_products = 3
        limit_capsules = 6

        products = Product.query.order_by(
            func.rand()).limit(limit_products).all()

        products = Product.query.order_by(
            func.rand()).limit(limit_products).all()

        for p in products:
            me_capsules = [x.capsule_id for x in p.capsules]
            tot_capsules = len(me_capsules)
            capsules = Capsule.query.filter(
                ~Capsule.id.in_(me_capsules)).limit(
                    (limit_capsules - tot_capsules)).all()
            choices = [c.id for c in capsules] + me_capsules
            shuffle(choices)
            questions.append({'product_id': p.id, 'name': p.name,
                              'choices': choices,
                              'capsule_count': tot_capsules})
        data = {}
        data['title'] = 'Cuestionario'
        data['questions'] = questions
        if settings.XSRF_COOKIES:
            data['csrf_token'] = generate_csrf_token()
        return self.render_template('game.html', **data)

    @authenticated
    def post(self):

        if settings.XSRF_COOKIES:
            csrf_protect()

        wins = 0
        result = ''
        querystring = ''
        answers = request.form.get('resp')

        if answers:
            data = set_format_data(answers)
            if data:
                for x in data:
                    pid = x.get('pid')
                    choices = x.get('choices')
                    p = Product.query.get(pid)
                    p_choices = [x.capsule_id for x in p.capsules]
                    if choices:
                        if choices == p_choices:
                            result += ' ' + str(pid) + ':1'
                            wins += 1
                        else:
                            result += ' ' + str(pid) + ':0'
                    else:
                        result += ' ' + str(pid) + ':0'

                uid = self.current_user.id
                attempts = UserGame.query.filter_by(
                    user_id=uid).count()

                game = UserGame()
                game.user_id = uid
                game.answers = answers
                game.results = result.strip()
                game.winner = True if wins == 3 else False
                game.attempts = attempts + 1
                db_session.add(game)

                try:
                    db_session.commit()
                    querystring = '?result=%s' % str(game.id)
                except Exception as exc:
                    logger.error(exc)
                    db_session.rollback()
                else:
                    logger.info('save game')
                db_session.remove()
        _redirect = 'thanks' if wins == 3 else 'retry'
        return redirect(url_for(_redirect) + querystring)
