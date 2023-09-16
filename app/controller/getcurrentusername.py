"""Module to get current logged in user."""

from flask_login import current_user

def getcurrentusername():
    """_summary_

    Returns:
        _type_: _description_
    """

    currentusername = current_user.username

    return currentusername
