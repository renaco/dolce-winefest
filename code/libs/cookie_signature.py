import hmac
import time
import base64
import hashlib
import json


def json_encode(value):
    """JSON-encodes the given Python object."""
    # JSON permits but does not require forward slashes to be escaped.
    # This is useful when json data is emitted in a <script> tag
    # in HTML, as it prevents </script> tags from prematurely terminating
    # the javscript.  Some json libraries do this escaping by default,
    # although python's standard library does not, so we do it here.
    # http://stackoverflow.com/questions/1580647/json-why-are-forward-slashes-escaped
    return json.dumps(value).replace("</", "<\\/")


def json_decode(value):
    """Returns Python objects for the given JSON string."""
    return json.loads(to_basestring(value))



def _time_independent_equals(a, b):
    if len(a) != len(b):
        return False
    result = 0
    if isinstance(a[0], int):
        # python3 byte strings
        for x, y in zip(a, b):
            result |= x ^ y
    else:
        # python2
        for x, y in zip(a, b):
            result |= ord(x) ^ ord(y)
    return result == 0


def _create_signature(secret, *parts):
    #hash = hmac.new(utf8(secret), digestmod=hashlib.sha1)
    hash = hmac.new(secret, digestmod=hashlib.sha1)
    for part in parts:
        hash.update(part)
    return hash.hexdigest()


def create_signed_value(secret, name, value):
    timestamp = str(int(time.time()))
    value = base64.b64encode(value)
    signature = _create_signature(secret, name, value, timestamp)
    value = "|".join([value, timestamp, signature])
    return value


def decode_signed_value(secret, name, value, max_age_days=31):
    if not value:
        return None

    parts = value.split("|")

    print parts

    if len(parts) != 3:
        return None
    signature = _create_signature(secret, name, parts[0], parts[1])
    if not _time_independent_equals(parts[2], signature):
        return None
    timestamp = int(parts[1])
    if timestamp < time.time() - max_age_days * 86400:
        return None
    if timestamp > time.time() + 31 * 86400:
        # _cookie_signature does not hash a delimiter between the
        # parts of the cookie, so an attacker could transfer trailing
        # digits from the payload to the timestamp without altering the
        # signature. For backwards compatibility, sanity-check timestamp
        # here instead of modifying _cookie_signature.
        return None
    if parts[1].startswith(b"0"):
        return None
    try:
        return base64.b64decode(parts[0])
    except Exception:
        return None


if __name__ == '__main__':
    cookie_secret = 'abc'
    jo = create_signed_value(cookie_secret, 'user', 'ro123_')
    print decode_signed_value(cookie_secret, 'user', jo)

