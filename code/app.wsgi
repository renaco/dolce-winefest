activate_this = '/home/macfri/projects/dolce-wine-fest/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
import sys
sys.path.insert(0, '/home/macfri/projects/dolce-wine-fest/src/code')
from server import app as application
