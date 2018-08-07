from flask import Blueprint


pages = Blueprint('pages', __name__)


@pages.route('/about')
def about():
    """about"""
    return 'about api'
