import settings

from flask import Flask
from urls import app_register_routes

app = Flask(__name__)

app.debug = settings.DEBUG
app.secret_key = settings.SECRET_KEY
app.pickle_based = True

app_register_routes(app)

if __name__ == '__main__':
    app.run(host=settings.HOST, port=settings.PORT)
