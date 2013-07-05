from controllers import RequestHandler
from models import User


class Login(RequestHandler):

    def get(self, status_code=None):
        if self.current_user:
            self.redirect(self.reverse_url('admin_project_main'))
            return

        self.render('admin/login.html', status_code=status_code)

    def post(self):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)

        if username and password:
            user = User.objects(username=username).first()

            if user and user.validate_password(password):
                self.set_secure_cookie('user', str(user.id))
                self.redirect(
                    self.get_argument(
                        'next', self.reverse_url('admin_project_main')))
                return

        self.get(1)


class Logout(RequestHandler):

    def get(self):
        self.clear_all_cookies()
        self.redirect(self.reverse_url('admin_login'))
