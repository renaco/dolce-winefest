import settings

from flask import Flask
from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.admin import Admin, BaseView, expose

from database import db_session
from models import (User, Product, Capsule, UserGame,
                    Department, ProductCapsule, SystemUser)

from forms import LoginForm
from flask import (redirect, flash, session, render_template,
                   url_for, request, Response, abort)

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
    users_count_active = User.query.filter_by(enabled=True).count()
    users_count_inactive = User.query.filter_by(enabled=False).count()

    users_count_play = db_session.query(
        func.count(func.distinct(User.id))
    ).join(UserGame, User.id == UserGame.user_id).scalar()

    games_per_day = db_session.query(
        func.count(UserGame.id).label('count'),
        func.date(UserGame.created_at).label('date')
    ).group_by(func.date(UserGame.created_at))

    games_last_days = db_session.query(
        func.dayname(UserGame.created_at).label('day'),
        func.count(UserGame.id).label('count')
    ).filter(
        func.week(UserGame.created_at) == func.week(func.now())
    ).group_by(
        func.dayname(UserGame.created_at)
    )

    data = []
    for x in games_last_days:
        data.append((x.day, x.count))

    return Response(stream_template('admin/stats.html',
                    users_count=users_count,
                    users_count_active=users_count_active,
                    users_count_inactive=users_count_inactive,
                    users_count_play=users_count_play,
                    games_per_day=games_per_day, data=data))


class LogoutView(BaseView):

    @expose('/')
    def index(self):
        session.pop('user_id')
        return redirect(settings.HOME_URL + 'admin/login')
     
class StatsView(BaseView):

    @expose('/')
    def index(self):

        # count
        users_count = User.query.count()
        users_count_complete = User.query.filter_by(enabled=True).count()
        users_count_incomplete = User.query.filter_by(enabled=False).count()

        users_count_games = db_session.query(
            func.count(func.distinct(User.id))
        ).join(UserGame).scalar()

        count_games = db_session.query(
            func.count(UserGame.id)
        ).join(User, User.id == UserGame.user_id).scalar()

        users_count_winner = db_session.query(func.count(
            func.distinct(User.id))
        ).join(UserGame, User.id == UserGame.user_id).filter(
        UserGame.winner == True).scalar()

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

        users_complete = users.filter(User.enabled == True).group_by(
            func.date(User.created_at))

        users_incomplete = users.filter(User.enabled == False).group_by(
            func.date(User.created_at))

        users_games = db_session.query(
            func.count(func.distinct(User.id)).label('count'),
            func.date(UserGame.created_at).label('date')
        ).join(UserGame).group_by(func.date(UserGame.created_at))


        users_winners = db_session.query(
            func.count(func.distinct(User.id)).label('count'),
            func.date(UserGame.created_at).label('date')
        ).filter(UserGame.winner == True).join(UserGame).group_by(func.date(UserGame.created_at))


        games = db_session.query(
            func.count(UserGame.id).label('count'),
            func.date(UserGame.created_at).label('date')
        ).join(User).group_by(func.date(UserGame.created_at))

        _users_games_week = db_session.query(
            func.dayname(UserGame.created_at).label('date'),
            func.count(UserGame.id).label('count')
        ).filter(
            func.week(UserGame.created_at) == func.week(func.now())
        ).group_by(
            func.dayname(UserGame.created_at)
        )

        users_games_week = [(x.date, x.count) for x in _users_games_week]

        return self.render('admin/stats.html',
                           count=dict(users=users_count,
                           complete=users_count_complete,
                           incomplete=users_count_incomplete,
                           user_games=users_count_games,
                           games=count_games,
                           winner=users_count_winner),
                           data=dict(users=_users,
                           complete=users_complete,
                           incomplete=users_incomplete,
                           users_games=users_games,
                           games=games,
                           week=users_games_week,
                           winners=users_winners))



class CapsuleView(ModelView):
    def __init__(self, session, **kwargs):
        super(CapsuleView, self).__init__(Capsule, session, **kwargs)

    def is_accessible(self):
        if not 'user_id' in session:
            abort(401)
        return True


class ProductCapsuleView(ModelView):

    def __init__(self, session, **kwargs):
        super(ProductCapsuleView, self).__init__(ProductCapsule, session, **kwargs)

    def is_accessible(self):
        if not 'user_id' in session:
            abort(401)
        return True


class DepartmentView(ModelView):

    def __init__(self, session, **kwargs):
        super(DepartmentView, self).__init__(Department, session, **kwargs)

    def is_accessible(self):
        if not 'user_id' in session:
            abort(401)
        return True

class UserGameView(ModelView):

    column_display_pk = True
    can_create = False
    column_list = ('answers', 'results', 'attempts', 'winner',
                   'created_at', 'user.first_name', 'user.last_name',
                   'user.fb_id')

    fast_mass_delete = True
    column_auto_select_related = True
    column_display_all_relations = True

    def __init__(self, session, **kwargs):
        super(UserGameView, self).__init__(UserGame, session, **kwargs)
    def is_accessible(self):
        if not 'user_id' in session:
            abort(401)
        return True

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

    inline_models = ((UserGame, ))
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

    def is_accessible(self):
        if not 'user_id' in session:
            abort(401)
        return True

class ProductView(ModelView):

    inline_models = ((ProductCapsule, ))

    def __init__(self, session, **kwargs):
        super(ProductView, self).__init__(Product, session, **kwargs)
    
    def is_accessible(self):
        if not 'user_id' in session:
            abort(401)
        return True

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


@app.route('/users_winners.csv')
def users_winners():
    def generate():
        users = db_session.query(User.first_name,
                                 User.last_name,
                                 case([(User.email != None,
                                 User.email)], else_=''),
                                 case([(User.dni != None,
                                 User.dni)], else_=''),
                                 case([(User.phone != None,
                                 User.phone)], else_=''),
                                 case([(Department.name != None,
                                 Department.name)], else_=''),
                                 func.date_format(User.created_at,
                                 '%Y-%m-%d %H:%i:%s')
                                 ).outerjoin(Department).join(
                                    UserGame).filter(
                                    UserGame.winner == True
                                    ).group_by(UserGame.user_id)

        row_columns = ('Name', 'Lastname', 'Email', 'Dni',
                       'Phone', 'Department', 'Created_at',)

        yield ','.join(row_columns) + '\n'
        for row in users.all():
            yield ','.join(row) + '\n'
    return Response(generate(), mimetype='text/csv')


@app.route('/game_export.csv')
def game_export():

    enabled = request.args.get('enabled')

    def generate():
        users = db_session.query(User.first_name,
                                 User.last_name,
                                 User.email,
                                 User.dni,
                                 User.phone,
                                 func.concat(UserGame.attempts, ''),
                                 case([(UserGame.winner == True,
                                 'si')],
                                 else_='no'),
                                 Department.name,
                                 func.date_format(UserGame.created_at,
                                 '%Y-%m-%d %H:%i:%s')
                                 ).join(Department).join(UserGame)

        row_columns = ('Name', 'Lastname', 'Email', 'Dni',
                       'Phone', 'Intentos', 'Ganador', 'Department',
                       'Created_at',)

        yield ','.join(row_columns) + '\n'

        if enabled:
            if enabled == '1':
                users = users.filter(User.enabled == True)
            if enabled == '0':
                users = users.filter(User.enabled == False)

        for row in users.all():
            yield ','.join(row) + '\n'
    return Response(generate(), mimetype='text/csv')


@app.route('/login/', methods=['GET', 'POST'])
def index():

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


admin = Admin(app,
              name="PAPA EXTRAORDINARIO - DOLCE",
              url='/',
              static_url_path='/static/')

admin.add_view(UserView(db_session))
admin.add_view(UserGameView(db_session))
admin.add_view(ProductView(db_session))
admin.add_view(CapsuleView(db_session))
admin.add_view(DepartmentView(db_session))
admin.add_view(ProductCapsuleView(db_session))
admin.add_view(StatsView())
admin.add_view(LogoutView())

if __name__ == '__main__':
    app.run()
