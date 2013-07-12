DEBUG = False
DATABASE_DEBUG = DEBUG
DATABASE_DSN = 'mysql://user_winefest:dw1n3fest@localhost/dolcegusto_winefest'

XSRF_COOKIES = True
SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
COOKIE_SECRET = "fsdklflsdjflt3434n434nr43nr34kn345345n34kl5kl34534534l"

HOST = '127.0.0.1'
PORT = 5000
DOMAIN_URL = ''

FACEBOOK_API_KEY = '129567663916076'
FACEBOOK_API_SECRET = 'e83a07baf96b5a9683bc403dcfc21edb'
FACEBOOK_DEBUG_TOKEN = ''
FACEBOOK_OAUTH = 'https://www.facebook.com/dialog/oauth/'
FACEBOOK_GRAPH = 'https://graph.facebook.com/'
FACEBOOK_CANVAS_PAGE = 'https://apps.facebook.com/129567663916076/'
FACEBOOK_ACCESS_TOKEN = 'https://graph.facebook.com/oauth/access_token'

STATIC_URL = '/static/'
HOME_URL = ''
#P3P_COMPACT = 'policyref="%s%sP3P/p3p.xml", CP="NON DSP COR CURa TIA"' % (
#    DOMAIN_URL, STATIC_URL)

P3P_COMPACT = 'policyref="%s%sP3P/p3p.xml", CP="NOI ADM DEV PSAi COM NAV OUR OTR STP IND DEM"' % (
    DOMAIN_URL, STATIC_URL)
try:
    from local_settings import *
except ImportError:
    pass
