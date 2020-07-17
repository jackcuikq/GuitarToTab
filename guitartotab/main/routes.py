from flask import render_template, request, Blueprint
from guitartotab.models import Tab
from flask_login import current_user

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/landing')
def landing():
    return render_template('landing.html', title='Landing')

@main.route('/about')
def about():
    return render_template('about.html', title='About')

@main.route('/my_tabs')
def my_tabs():
    page = request.args.get('page', 1, type=int)
    user = current_user
    tabs = Tab.query.filter_by(author=user).order_by(Tab.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template('home.html', title='My Tabs', tabs=tabs)
