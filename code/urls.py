from controllers import user, views, comment


def app_register_routes(app):

    app.add_url_rule(
        '/',
        view_func=views.Home.as_view('home')
    )
    app.add_url_rule(
        '/user/validator',
        view_func=user.Validator.as_view('user_validator')
    )
    app.add_url_rule(
        '/form',
        view_func=user.Register.as_view('form')
    )
    app.add_url_rule(
        '/add_comment',
        view_func=comment.Add.as_view('add_comment')
    )
    app.add_url_rule(
        '/terms',
        view_func=views.Terms.as_view('terms')
    )
    app.add_url_rule(
        '/thanks',
        view_func=views.Thanks.as_view('thanks')
    )
    app.add_url_rule(
        '/winners',
        view_func=views.Winners.as_view('winners')
    )
    app.add_url_rule(
        '/nofan',
        view_func=views.NoFan.as_view('nofan')
    )
    app.add_url_rule(
        '/fan',
        view_func=views.Fan.as_view('fan')
    )
    app.add_url_rule(
        '/download.csv',
        view_func=views.Download.as_view('download')
    )
