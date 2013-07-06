import sys
from os.path import abspath, dirname

root = abspath('../../') 
current_path = abspath(dirname(__file__))
root = __file__.replace('src/code/app.wsgi', '')

activate_this = root + '/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
sys.path.insert(0, current_path)
from server import app as application
