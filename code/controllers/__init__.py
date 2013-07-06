import uuid
import settings

from flask import (request, session, abort,
                   make_response, render_template)


def csrf_protect(action=''):
    if request.method == "POST":
        token = session.pop('%s_csrf_token' % action, None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)


def generate_csrf_token(action=''):
    session['%s_csrf_token' % action] = '%s%s' % (
        str(uuid.uuid4()),
        settings.COOKIE_SECRET)
    return session['%s_csrf_token' % action]


class RequestHandler(object):

    def render_template(self, name, **kwargs):
        r = make_response(render_template(name, **kwargs))
        r.headers["P3P"] = settings.P3P_COMPACT
        return r
