import logging
import settings

from flask.views import MethodView
from flask import request, redirect, session, url_for

from controllers import (RequestHandler, csrf_protect)

from models import User
from database import db_session


class Add(MethodView, RequestHandler):

    def post(self):

        #if settings.XSRF_COOKIES:
            #csrf_protect('home')

        comment = request.form['comment']

        if not comment:
            logging.error('not comment')
            return redirect(url_for('home'))

        if len(comment) > 140:
            logging.error('not size comment')
            return redirect(url_for('home'))

        """
        user = User()
        user.comment = comment
        db_session.add(user)

        try:
            db_session.commit()
        except Exception as exc:
            logging.error(exc)
            db_session.rollback()
            db_session.remove()
            return redirect(url_for('home'))
        else:
            db_session.remove()
        """
        if 'comment' in session:
            session.pop('comment')
        session['comment'] = comment

        return redirect(url_for('form'))
