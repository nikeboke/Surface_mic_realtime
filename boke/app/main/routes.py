from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
import numpy as np
import jwt
import datetime

from app import db, bcrypt
from app.models import User

main = Blueprint('main', __name__)

host = 'http://127.0.0.1:5000'
@main.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    script, div, cdn_js = plot()
    return render_template('home.html', script=script, div=div, cdn_js=cdn_js)


@main.route('/', methods=['GET', 'POST'])
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    #token = jwt.encode({'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, current_app.config['SECRET_KEY'])
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and bcrypt.check_password_hash(user.password, request.form.get('password')):
            login_user(user, remember=True)
            return redirect(url_for('main.home'))
        flash('Invalid name or password', 'error')

    return render_template('login.html', title='Log in')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user:
            flash('Username already taken!', 'error')
        elif request.form.get('password') == request.form.get('confirm_password'):
            hashed_pw = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
            user = User(username=request.form.get('username'), password=hashed_pw)
            db.session.add(user)
            db.session.commit()
            flash('Created new account', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('passwords must be same', 'error')

    return render_template('signup.html', title='Sign up')


@main.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('main.login'))



@main.route('/events', methods=['GET', 'POST'])
@login_required
def events():
    from app.apis.events import Event, get_devices, actions, trigs
    events = Event.get_events()
    names = get_devices()
    return render_template('events.html', title='events', events=events, device_names=names, trigs=trigs, acts=actions)

def plot():
    from bokeh.models import AjaxDataSource, CustomJS
    from bokeh.plotting import figure
    from bokeh.resources import CDN
    from bokeh.embed import components
    from bokeh.layouts import gridplot

    sound_adapter = CustomJS(code="""
    const result = {x: [], y: []}
    const pts = cb_data.response.points
    for (let i=0; i<pts.length; i++) {
        result.x.push(pts[i][0])
        result.y.push(pts[i][1])
    }
    return result
    """)

    sound_source = AjaxDataSource(data_url=f'{host}{url_for("data.get_data")}', polling_interval=200, adapter=sound_adapter, mode='replace')

    sound_plot = figure(output_backend='webgl', y_range=(-(2**15), 2**15))
    sound_plot.line('x', 'y', source=sound_source)
    #sound_plot.xaxis.visible = False
    #sound_plot.yaxis.visible = False

    pred_adapter = CustomJS(code="""
    const result = {x:[], y: []}
    const pts = cb_data.response.points
    for (let i=0; i<pts.length; i++) {
        result.x.push(i)
        result.y.push(pts[i])
    }

    return result
    """)


    pred_source = AjaxDataSource(data_url=f'{host}{url_for("data.predict")}', polling_interval=100, adapter=pred_adapter, max_size=100, mode='replace')
    pred_plot = figure(output_backend="webgl", y_range=(0, 6), title='Proba')
    pred_plot.vbar(x='x', top='y', source=pred_source, color='blue', width=0.2)
        #pred_plot.xaxis.visible = False

    p = gridplot([[sound_plot, pred_plot]])

    script, div = components(p)
    cdn_js = CDN.js_files
    return script, div, cdn_js


