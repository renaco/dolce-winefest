#activate_this = '/home/macfri/projects/dolce-padre/bin/activate_this.py'
activate_this = '/var/www/nestle-peru.com/dolcegusto/fb/diadelpadre-2013/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
import sys
#sys.path.insert(0, '/home/macfri/projects/dolce-padre/src/code')
sys.path.insert(0, '/var/www/nestle-peru.com/dolcegusto/fb/diadelpadre-2013/src/code')
from server import app as application
