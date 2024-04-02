"""Module to get all projects name created by the current active user."""

from flask import flash
from app.controller import (
    life_logging
)
from pprint import pformat

logger = life_logging.get_logger()

def getcurrentuserprojects(current_username, userprojects):
    """
    INPUT:
        current_username: name of the current active user
        userprojects: instance of 'userprojects' collection

    OUTPUT:
        userprojectsname: sorted list of current user projects name
    """

    userprojectsname = []
    try:
        # logger.debug(current_username)
        userprojects  = userprojects.find_one({ 'username' : current_username })
        myproject = userprojects['myproject']
        myprojectlist = list(myproject.keys())
        projectsharedwithme = userprojects['projectsharedwithme']
        projectsharedwithmelist = list(projectsharedwithme.keys())
        # userprojectsname = set(myproject + projectsharedwithme)
        userprojectsname = set(myprojectlist + projectsharedwithmelist)
    except:
        logger.exception("")
        flash('Please create your first project.')
    # logger.debug('userprojectsname: %s', pformat(userprojectsname))
    return sorted(list(userprojectsname))
