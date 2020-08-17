from flask import (Blueprint, render_template, url_for, flash, redirect,
                    request, abort, current_app)
from flask_login import current_user, login_required
from guitartotab import db
from guitartotab.models import Tab
from guitartotab.tabs.forms import TabForm
from guitartotab.AudioToTab import *
from werkzeug.utils import secure_filename
import os
import librosa

tabs = Blueprint('tabs', __name__)

@tabs.route('/tab/new', methods=['GET', 'POST'])
@login_required
def new_tabs():
    form = TabForm()
    if form.validate_on_submit():
        audio = request.files['file']
        filename = secure_filename(audio.filename)
        audio.save(os.path.join(current_app.root_path, 'static/tab_audio', filename))

        y, sr = librosa.load(os.path.join(current_app.root_path, 'static/tab_audio', filename))
        
        tab_content = AudioToTab(y, sr)   

        tab = Tab(title=form.title.data, content=tab_content, author=current_user)
        db.session.add(tab)
        db.session.commit()
        return redirect(url_for('main.my_tabs'))
        
    #return render_template('create_tab.html', title='New Tab', form=form, legend='New Tab')
    return render_template('tab_audio.html', title='Record or Upload Audio', form=form)

@tabs.route('/tab/<int:tab_id>')
def tab(tab_id):
    tab = Tab.query.get_or_404(tab_id)
    return render_template('tab.html', title=tab.title, tab=tab)


@tabs.route('/tab/<int:tab_id>/update', methods=['GET', 'POST'])
@login_required
def update_tab(tab_id):
    tab = Tab.query.get_or_404(tab_id)

    form = TabForm()
    if form.validate_on_submit():
        tab.title = form.title.data
        tab.content = form.content.data
        db.session.commit()
        flash('Your tab has been updated!', 'success')
        return redirect(url_for('tabs.tab', tab_id=tab.id))

    elif request.method == 'GET':
        form.title.data = tab.title
        form.content.data = tab.content

    return render_template('create_tab.html', title='Update Tab', form=form, legend='Update Tab')


@tabs.route('/tab/<int:tab_id>/delete', methods=['POST'])
@login_required
def delete_tab(tab_id):
    tab = Tab.query.get_or_404(tab_id)

    db.session.delete(tab)
    db.session.commit()
    flash('Your tab has been deleted!', 'success')
    return redirect(url_for('main.my_tabs'))
