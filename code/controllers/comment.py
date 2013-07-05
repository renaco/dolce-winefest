import logging
import settings

from flask.views import MethodView
from flask import request, redirect, session, url_for

from controllers import (RequestHandler, csrf_protect)


class Add(MethodView, RequestHandler):

    def post(self):

        if settings.XSRF_COOKIES:
            logging.error('not csrf_protect')
            csrf_protect()

        comment = request.form['comment']

        if not comment:
            logging.error('not comment')
            return redirect(url_for('home'))

        if len(comment) > 140:
            logging.error('not size comment')
            return redirect(url_for('home'))

        if 'comment' in session:
            session.pop('comment')
        session['comment'] = comment
        return redirect(url_for('form'))
