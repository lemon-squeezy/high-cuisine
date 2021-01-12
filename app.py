#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from flask import Flask, flash, render_template, redirect, request, \
    session, url_for

from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, \
    check_password_hash
from functools import wraps
from datetime import datetime

if os.path.exists('env.py'):
    import env

app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.secret_key = os.environ.get('SECRET_KEY')

mongo = PyMongo(app)

# --- Date Variable --- #

current_date = datetime.today().strftime('%d.%m.%Y')


# throws users that are not logged in to Login page if they try to access certain pages

def login_required(f):

    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))

    return wrap


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/recipes')
def recipes():
    recipes = list(mongo.db.recipes.find())
    return render_template('recipes.html', recipes=recipes)


@app.route('/basics')
def basics():
    return render_template('basics.html')


@app.route('/shop')
def shop():
    return render_template('shop.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form.get('query')
    recipes = list(mongo.db.recipes.find({'$text': {'$search': query}}))
    return render_template('recipes.html', recipes=recipes)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        # Check if username already exists in Database

        existing_user = \
            mongo.db.users.find_one({'username': request.form.get('username'
                                    ).lower()})

        if existing_user:
            flash('Username already exists - Try another one!')
            return redirect(url_for('register'))

        register = {'email': request.form.get('email').lower(),
                    'username': request.form.get('username').lower(),
                    'password': generate_password_hash(request.form.get('password'
                    ))}
        mongo.db.users.insert_one(register)

        # Put user into a 'session' cookie

        session['user'] = request.form.get('username').lower()
        flash('Registration Successful! You can now share your own recipes!'
              )
        return redirect(url_for('profile', username=session['user']))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        # check if username exists in db

        existing_user = \
            mongo.db.users.find_one({'username': request.form.get('username'
                                    ).lower()})

        if existing_user:

            # ensure hashed password matches user input

            if check_password_hash(existing_user['password'],
                                   request.form.get('password')):
                session['user'] = request.form.get('username').lower()
                return redirect(url_for('profile',
                                username=session['user']))
            else:

                # invalid password match

                flash('Incorrect Username and/or Password')
                return redirect(url_for('login'))
        else:

            # username doesn't exist

            flash('Incorrect Username and/or Password')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():

    # grab the session user's username from db

    username = mongo.db.users.find_one({'username': session['user'
            ]})['username']
    if session['user']:
        recipes = mongo.db.recipes.find({'created_by': username}).sort("recipe_name", 1)
        return render_template('profile.html', username=username,
                               recipes=recipes)
    return redirect(url_for('login'))


@app.route('/logout')
def logout():

    # remove user from session cookies

    flash('You have been logged out')
    session.pop('user')
    return redirect(url_for('login'))


# ---- RECIPE PAGES ----- #

@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        recipe = {
            'category_name': request.form.get('category_name'),
            'recipe_name': request.form.get('recipe_name'),
            'recipe_time_prep': request.form.get('recipe_time_prep'),
            'recipe_time_cook': request.form.get('recipe_time_cook'),
            'recipe_serves': request.form.get('recipe_serves'),
            'recipe_difficulty': request.form.get('recipe_difficulty'),
            'img_url': request.form.get('img_url'),
            'recipe_ingredients': request.form.get('recipe_ingredients'
                    ),
            'recipe_method': request.form.get('recipe_method'),
            'created_by': session['user'],
            'date_added': current_date,
            }
        mongo.db.recipes.insert_one(recipe)
        flash('Recipe Successfully Added')
        return redirect(url_for('recipes'))

    categories = mongo.db.categories.find().sort('category_name', 1)
    return render_template('add_recipe.html', categories=categories)


@app.route('/recipe/<recipe_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    if request.method == 'POST':
        submit = {
            'category_name': request.form.get('category_name'),
            'recipe_name': request.form.get('recipe_name'),
            'recipe_time_prep': request.form.get('recipe_time_prep'),
            'recipe_time_cook': request.form.get('recipe_time_cook'),
            'recipe_serves': request.form.get('recipe_serves'),
            'recipe_difficulty': request.form.get('recipe_difficulty'),
            'img_url': request.form.get('img_url'),
            'recipe_time': request.form.get('recipe_time'),
            'recipe_ingredients': request.form.get('recipe_ingredients'
                    ),
            'recipe_method': request.form.get('recipe_method'),
            'created_by': session['user'],
            'date_added': current_date,
            }
        mongo.db.recipes.update({'_id': ObjectId(recipe_id)}, submit)
        flash('Recipe Successfully Updated')

    recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    categories = mongo.db.categories.find().sort('category_name', 1)
    return render_template('edit_recipe.html', recipe=recipe,
                           categories=categories)


# Delete Recipe

@app.route('/recipe/<recipe_id>/delete')
@login_required
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({'_id': ObjectId(recipe_id)})
    flash('Recipe Successfully Deleted')
    return redirect(url_for('recipes'))


# View recipe information function

@app.route('/recipe/<recipe_id>/view', methods=['GET'])
def view_recipe(recipe_id):
    """Find recipe by id and direct to view recipe page"""

    recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template('view_recipe.html', recipe=recipe)


# Terms

@app.route('/terms')
def terms():
    return render_template('terms.html')


# Errors

@app.errorhandler(404)
def page_not_found(e):
    return (render_template('404.html'), 404)


@app.errorhandler(500)
def internal_error(error):
    return (render_template('500.html'), 500)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT'
            )), debug=True)
