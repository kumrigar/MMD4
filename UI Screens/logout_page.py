from flask import Blueprint, session, redirect, url_for

logout_blueprint = Blueprint('logout', __name__)

@logout_blueprint.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login.login'))
