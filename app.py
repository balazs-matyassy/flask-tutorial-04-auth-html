from flask import Flask, render_template, abort, request, flash, redirect, url_for, g, session, current_app

import model
import security
from security import is_fully_authenticated
from config import Config
from model import (Recipe, find_all, find_by_id, find_by_name,
                   save, delete_by_id)

app = Flask(__name__)
app.config.from_object(Config)

model.init_app(app)
security.init_app(app)


@app.route('/login', methods=('GET', 'POST'))
def login():
    if g.username:
        return redirect(url_for('list_all'))

    username = ''
    password = ''
    errors = []

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if username == '':
            errors.append('Username missing.')

        if password == '':
            errors.append('Password missing.')

        if len(errors) == 0:
            if username.lower() == current_app.config['ADMIN_USERNAME'].lower() \
                    and password == current_app.config['ADMIN_PASSWORD']:
                session['logged_in'] = True
                flash('Login successful.')

                return redirect(url_for('list_all'))
            else:
                errors.append('Wrong username or password.')

    return render_template(
        'login.html',
        username=username,
        password=password,
        errors=errors
    )


@app.route('/logout')
def logout():
    session.clear()
    flash('Logout successful.')

    return redirect(url_for('list_all'))


@app.route('/')
def list_all():
    if request.args.get('search'):
        recipes = find_by_name(request.args.get('search'))
    else:
        recipes = find_all()

    return render_template('list.html', recipes=recipes)


@app.route('/view/<int:recipe_id>')
def view(recipe_id):
    recipe = find_by_id(recipe_id) or abort(404)

    return render_template('view.html', recipe=recipe)


@app.route('/create', methods=('GET', 'POST'))
@is_fully_authenticated
def create():
    recipe = Recipe()
    errors = []

    if request.method == 'POST':
        recipe.update(request.form)
        errors = recipe.validate()

        if len(errors) == 0:
            save(recipe)
            flash('Recipe created.')

            return redirect(url_for('list_all'))

    return render_template(
        'form.html',
        recipe=recipe,
        errors=errors
    )


@app.route('/edit/<int:recipe_id>', methods=('GET', 'POST'))
@is_fully_authenticated
def edit(recipe_id):
    recipe = find_by_id(recipe_id) or abort(404)
    errors = []

    if request.method == 'POST':
        recipe.update(request.form)
        errors = recipe.validate()

        if len(errors) == 0:
            save(recipe)
            flash('Recipe saved.')

            return redirect(url_for('edit', recipe_id=recipe.recipe_id))

    return render_template(
        'form.html',
        recipe=recipe,
        errors=errors
    )


@app.route('/delete/<int:recipe_id>', methods=('POST',))
@is_fully_authenticated
def delete(recipe_id):
    find_by_id(recipe_id) or abort(404)
    delete_by_id(recipe_id)
    flash('Recipe deleted.')

    return redirect(url_for('list_all'))


if __name__ == '__main__':
    app.run()
