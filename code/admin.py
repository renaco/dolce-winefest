import settings

from flask import Flask
from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.admin import Admin, BaseView, expose

from database import db_session
from models import (User, Department, SystemUser)

from forms import LoginForm
from flask import (redirect, flash, session, render_template,
                   request, Response, abort)

from sqlalchemy import func, case


app = Flask(__name__)
app.debug = True
app.secret_key = settings.SECRET_KEY


@app.teardown_request
def remove_db_session(exception=None):
    db_session.remove()


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv


@app.route('/stats.html')
def render_large_template():
    users_count = User.query.count()
  
    return Response(stream_template('admin/stats.html',
                    users_count=users_count,
                    ))


"""
class LogoutView(BaseView):

    @expose('/')
    def index(self):
        session.pop('user_id')
        return redirect(settings.HOME_URL + 'admin/login')
"""

class StatsView(BaseView):

    @expose('/')
    def index(self):

        # count
        users_count = User.query.count()

        # per day
        users = db_session.query(
            func.count(User).label('count'),
            func.date(User.created_at).label('date')
        )

        _users = db_session.query(
            func.count(User).label('count'),
            func.date(User.created_at).label('date')
        ).group_by(
            func.date(User.created_at))


        return self.render('admin/stats.html',
                           count=dict(users=users_count,
                           data=dict(users=_users,
                           )))




class DepartmentView(ModelView):

    def __init__(self, session, **kwargs):
        super(DepartmentView, self).__init__(Department, session, **kwargs)

    """
    def is_accessible(self):
        if not 'user_id' in session:
            abort(401)
        return True
    """

class UserView(ModelView):

    column_display_pk = True
    can_create = False
    column_list = ('first_name', 'last_name', 'email', 'dni',
                   'phone', 'enabled', 'department.name',
                   'created_at',)

    column_searchable_list = ('first_name', 'email')
    column_filters = ('first_name', 'email', 'enabled')
    action_disallowed_list = ['delete']

    form_choices = {'department.name': [
        ('db_value', 'display_value'),
    ]}

    fast_mass_delete = True
    column_auto_select_related = True
    column_display_all_relations = True
    column_display_all_relations = True

    form_widget_args = {
        'fb_id': {
            'style': 'color: black'
        }
    }

    def __init__(self, session, **kwargs):
        super(UserView, self).__init__(User, session, **kwargs)

    """
    def is_accessible(self):
        if not 'user_id' in session:
            abort(401)
        return True
    """

class UserExportView(BaseView):
    @expose('/')
    def index(self):
        enabled = request.args.get('enabled')

        def generate():
            users = db_session.query(User.first_name,
                                     User.last_name,
                                     User.email,
                                     User.dni,
                                     User.phone,
                                     case([(User.enabled == True,
                                     'completed')],
                                     else_='incomplete'),
                                     Department.name,
                                     func.date_format(User.created_at,
                                     '%Y-%m-%d %H:%i:%s')
                                     ).join(Department)

            if enabled:
                if enabled == '1':
                    users = users.filter(User.enabled == True)
                if enabled == '0':
                    users = users.filter(User.enabled == False)

            for row in users.all():
                yield ','.join(row) + '\n'
        return Response(generate(), mimetype='text/csv')


@app.route('/users_export.csv')
def users_export():
    enabled = request.args.get('enabled')

    def generate():
        users = db_session.query(User.first_name,
                                 User.last_name,
                                 case([(User.email != None,
                                 User.email)], else_=''),
                                 case([(User.dni != None,
                                 User.dni)], else_=''),
                                 case([(User.phone != None,
                                 User.phone)], else_=''),
                                 case([(User.enabled == '1', 'yes')],
                                 else_='no'),
                                 case([(Department.name != None,
                                 Department.name)], else_=''),
                                 func.date_format(User.created_at,
                                 '%Y-%m-%d %H:%i:%s')
                                 ).outerjoin(Department)

        row_columns = ('Name', 'Lastname', 'Email', 'Dni',
                       'Phone', 'Complete', 'Department', 'Created_at',)

        if enabled:
            if enabled == '1':
                users = users.filter(User.enabled == True)
            if enabled == '0':
                users = users.filter(User.enabled == False)

        yield ','.join(row_columns) + '\n'
        for row in users.all():
            yield ','.join(row) + '\n'
    return Response(generate(), mimetype='text/csv')


@app.route('/login/', methods=['GET', 'POST'])
def index():

    return redirect(settings.HOME_URL +  'admin/')

    """
    if 'user_id' in session:
        return redirect(settings.HOME_URL +  'admin/')

    error = None
    if request.method == 'POST':
        form = LoginForm(request.form)
        if form.validate():
            user = SystemUser.query.filter_by(
                username=form.username.data).first()
            if user and user.valid_password(form.password.data):
                session['user_id'] = user.id
                flash('Logged in successfully!', 'success')
                return redirect(settings.HOME_URL +  'admin/')
            else:
                error = 'Wrong username or password!'
    else:
        form = LoginForm()
    return render_template('admin/login.html',
                           form=form,
                           error=error,
                           is_admin=True)
    """


admin = Admin(app,
              name="PAPA EXTRAORDINARIO - DOLCE",
              #url='/',
              static_url_path='/static/')

admin.add_view(UserView(db_session))
admin.add_view(DepartmentView(db_session))
admin.add_view(StatsView())
#admin.add_view(LogoutView())

if __name__ == '__main__':
    app.run()
