import uuid
import settings

from flask import (request, session, abort,
                   make_response, render_template)


def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)


def generate_csrf_token():
    session['_csrf_token'] = '%s%s' % (
        str(uuid.uuid4()),
        settings.COOKIE_SECRET)
    return session['_csrf_token']


class RequestHandler(object):

    def render_template(self, name, **kwargs):
        r = make_response(render_template(name, **kwargs))
        r.headers["P3P"] = settings.P3P_COMPACT
        return r
