import functools

from flask import g, session, redirect, url_for, current_app


def init_app(app):
    app.before_request(__load_current_user)
    app.jinja_env.globals['is_fully_authenticated'] = lambda: g.username


def is_fully_authenticated(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.username is None:
            return redirect(url_for('login'))

        return view(**kwargs)

    return wrapped_view


def __load_current_user():
    if not session.get('logged_in'):
        g.username = None
    else:
        g.username = current_app.config.get('ADMIN_USERNAME')
