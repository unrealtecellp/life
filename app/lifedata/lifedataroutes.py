"""Module containing the routes for the data part of the LiFe."""
from flask import Blueprint, render_template, jsonify
from app import mongo
from app.controller import getdbcollections, getcurrentuserprojects, getcurrentusername

lifedata = Blueprint('lifedata', __name__, template_folder='templates', static_folder='static')

@lifedata.route('/', methods=['GET', 'POST'])
@lifedata.route('/home', methods=['GET', 'POST'])
def home():
    """_summary_

    Returns:
        _type_: _description_
    """
    print('lifedata home')

    return render_template("lifedatahome.html")

@lifedata.route('/getprojectslist', methods=['GET', 'POST'])
def getprojectslist():
    """_summary_
    """
    userprojects, = getdbcollections.getdbcollections(mongo, 'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    projectslist = getcurrentuserprojects.getcurrentuserprojects(current_username, userprojects)

    return jsonify(projectslist=projectslist)
