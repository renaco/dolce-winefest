import sys
import uuid
import settings
import logging

from functools import wraps
from flask import (request, session, abort,
                   make_response, render_template)

from models import User
from database import db_session

from libs.pagination import Paginator
from libs.facebook import get_fb_cookie, info, get_access_token_code


def logger(name):
    logging.basicConfig(format="""%(asctime)s -[ %(module)s.%(funcName)s in line: %(lineno)d ] - %(levelname)s - %(message)s - """, level=logging.DEBUG, stream=sys.stderr)
    log = logging.getLogger(name)
    return log


log = logger(__name__)


def authenticated(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if settings.FACEBOOK_DEBUG_TOKEN:
            token = settings.FACEBOOK_DEBUG_TOKEN

            fields = (
                'id',
                'first_name',
                'last_name',
                'email',
                'gender',
            )

            profile = info(token, ','.join(fields))
            if 'error' in profile:
                abort(401)
        else:
            parsed_request = get_fb_cookie()
            if not parsed_request:
                abort(401)
                log.info('not parsed_request')
        return f(*args, **kwargs)
    return decorated


def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)


def generate_csrf_token():
    session['_csrf_token'] = '%s%s' % (str(uuid.uuid4()),
                                           settings.COOKIE_SECRET)
    return session['_csrf_token']


class RequestHandler(object):

    def render_template(self, name, **kwargs):
        r = make_response(render_template(name, **kwargs))
        r.headers["P3P"] = settings.P3P_COMPACT
        return r

    @property
    def current_user(self):
        if not hasattr(self, "_current_user"):
            self._current_user = self.get_current_user()
        return self._current_user

    def get_current_user(self):
        token = profile = None
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'gender',
        )
        parsed_request = get_fb_cookie()
        log.info('parsed_request: %s' % parsed_request)

        if settings.FACEBOOK_DEBUG_TOKEN:
            token = settings.FACEBOOK_DEBUG_TOKEN
            profile = info(token, ','.join(fields))
            if 'error' in profile:
                log.error(profile.get('error'))
                abort(401)
            fb_id = profile['id']
        else:
            if not parsed_request:
                log.error('No parsed_request')
                abort(401)
            fb_id = parsed_request.get('user_id')

        if 'fb_id' in session:
            log.info('exists fb session')
            if session['fb_id'] == fb_id:
                log.info('session==cookie')
                __user = User.query.filter_by(fb_id=fb_id).first()
                if __user:
                    return __user
        user = User.query.filter_by(fb_id=fb_id).first()

        if not user:
            log.info('new user')
            if not profile:
                token = get_access_token_code('', parsed_request['code'])
                profile = info(token, ','.join(fields))
            return self._save_user(fb_id, token, profile)
        else:
            session['fb_id'] = fb_id
            log.info('exists user')
        return user

    def _save_user(self, fb_id, token, profile):
        user = User()
        user.fb_id = fb_id
        user.oauth_token = token
        user.first_name = profile.get('first_name')
        user.last_name = profile.get('last_name')
        user.fb_first_name = profile.get('first_name')
        user.fb_last_name = profile.get('last_name')
        user.fb_gender = profile.get('gender')
        user.fb_email = ''

        if profile.get('email'):
            if not "@proxymail.facebook" in profile.get('email'):
                user.fb_email = profile.get('email')
        db_session.add(user)
        try:
            db_session.commit()
        except Exception as exc:
            log.error(exc)
            db_session.rollback()
            db_session.remove()
            return None
        else:
            session['fb_id'] = fb_id
            log.info('save user')
            db_session.remove()
            return user


class ListMixin(object):

    @property
    def current_page(self):
        current_page = request.form.get('page', '1')
        return int(current_page) if current_page.isdigit() else 1

    def get_pagination(self, query, count, per_page=10):
        try:
            per_page = int(per_page)
        except ValueError:
            per_page = 10
        page = self.current_page
        paginator = Paginator(page=self.current_page, total_items=count,
                              per_page=per_page)
        per_page = paginator.per_page
        return {
            'items': query[(page - 1) * per_page: page * per_page],
            'pages': paginator.pages,
            'total_items': count,
            'current_page': page,
            'total_pages': paginator.total_pages,
        }
