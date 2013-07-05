import hmac
import urllib
import base64
import hashlib
import logging
import simplejson
import settings
from flask import session, request


def load_data_url(url, params, json=True):

    try:
        data = urllib.urlopen('%s?%s' % (
            url, urllib.urlencode(params))).read()
        if json:
            data = simplejson.loads(data)
    except Exception as exc:
        logging.error(exc)
        data = None
    return data


def js_windows_location(url):
    return "<script>top.location.href='%s'</script>" % url


def base64_url_decode(inp):
    padding_factor = (4 - len(inp) % 4) % 4
    inp += "=" * padding_factor

    return base64.b64decode(unicode(inp).translate(
        dict(zip(map(ord, u'-_'), u'+/'))))


def parse_signed_request(signed_request, secret):
    l = signed_request .split('.', 2)
    encoded_sig = l[0]
    payload = l[1]

    sig = base64_url_decode(encoded_sig)
    data = simplejson.loads(base64_url_decode(payload))

    if data.get('algorithm').upper() != 'HMAC-SHA256':
        logging.error('Unknown algorithm')
        return None
    else:
        expected_sig = hmac.new(
            secret, msg=payload, digestmod=hashlib.sha256
        ).digest()

    if sig != expected_sig:
        return None
    else:
        return data


def get_access_token_canvas():
    signed_request = request.form.get('signed_request')
    if signed_request:
        user = parse_signed_request(
            signed_request, settings.API_SECRET)
        if user and 'oauth_token' in user:
            access_token = user['oauth_token']
            if not 'oauth_token' in session:
                session['oauth_token'] = access_token
        else:
            return None
    else:
        if 'oauth_token' in session:
            access_token = session['oauth_token']
        else:
            return None
    return access_token


def get_access_token_code(redirect_uri, code):
    params = dict(
        client_id=settings.API_KEY,
        client_secret=settings.API_SECRET,
        redirect_uri=redirect_uri,
        code=code
    )
    data = load_data_url(
        url=settings.FACEBOOK_ACCESS_TOKEN,
        params=params,
        json=False
    )
    try:
        return data.split('&')[0].split('=')[1]
    except Exception as exc:
        logging.error(exc)
        return None


def get_fb_cookie():
    cookie = request.cookies.get('fbsr_%s' % settings.API_KEY, "")
    if not cookie:
        return None
    return parse_signed_request(cookie, settings.API_SECRET)


def auth(permissions, redirect_uri):
    params = dict(
        client_id=settings.API_KEY,
        redirect_uri=redirect_uri,
        scope=','.join(permissions),
    )
    url = '%s?%s' % (settings.FACEBOOK_OAUTH, urllib.urlencode(params))
    logging.info('url: %s' % url)
    return js_windows_location(url)


def info(access_token, fields):
    return load_data_url(
        url='%s/%s' % (settings.FACEBOOK_GRAPH, 'me'),
        params={'access_token': access_token, 'fields': fields},
        json=True
    )
