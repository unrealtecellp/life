"""Module to get the active project name of the current user"""

from app.controller import  (
    life_logging
)
logger = life_logging.get_logger()

def getactiveprojectname(current_username, userprojects_collection):
    """
    INPUT:
        current_username: name of the current active user.
        userprojects_collection: instance of 'userprojects_collection'.

    OUTPUT:
        activeprojectname: current user active project name
    """

    activeprojectname = userprojects_collection.find_one({ 'username' : current_username },\
                    {'_id' : 0, 'activeprojectname': 1})
    # logger.debug("activeprojectname: %s", activeprojectname)
    if len(activeprojectname) != 0:
        activeprojectname = activeprojectname['activeprojectname']
    else:
        activeprojectname = ''
        

    return activeprojectname
