"""Module containing the routes for the models part of the LiFe."""
from flask import Blueprint, render_template

lifemodels = Blueprint('lifemodels', __name__, template_folder='templates', static_folder='static')

@lifemodels.route('/', methods=['GET', 'POST'])
@lifemodels.route('/home', methods=['GET', 'POST'])
def home():
    """_summary_

    Returns:
        _type_: _description_
    """
    print('lifemodels home')

    return render_template("lifemodelshome.html")
