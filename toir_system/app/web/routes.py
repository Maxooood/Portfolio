from flask import render_template
from app.web import web_bp


@web_bp.route('/login')
def login():
    return render_template('login.html')


@web_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@web_bp.route('/requests')
def requests_list():
    return render_template('requests.html')


@web_bp.route('/requests/<int:req_id>')
def request_detail(req_id):
    return render_template('request_detail.html', req_id=req_id)


@web_bp.route('/equipment')
def equipment():
    return render_template('equipment.html')


@web_bp.route('/users')
def users():
    return render_template('users.html')


@web_bp.route('/analytics')
def analytics():
    return render_template('analytics.html')
