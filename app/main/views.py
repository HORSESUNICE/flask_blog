from flask import render_template, redirect, url_for
from . import main

@main.route('/')
def index():
    return render_template('blogbase.html')

@main.route('/epsilon')
def epsilon():
    return redirect(url_for('.index'))

@main.route('/resume')
def resume():
    return redirect(url_for('.index'))
