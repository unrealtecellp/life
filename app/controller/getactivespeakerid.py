"""Module to get the active speaker id of the current user"""

# def getactivespeakerid(userprojects, current_username):
#     """
#     INPUT:
#         current_username: name of the current active user
#         userprojects: instance of 'userprojects' collection

#     OUTPUT:
#         activespeakerid: current user active speaker id
#     """

#     activespeakerid = userprojects.find_one({ 'username' : current_username },\
#                         {'_id' : 0, 'activespeakerId': 1})
#     if len(activespeakerid) != 0:
#         activespeakerid = activespeakerid['activespeakerId']
#     else:
#         activespeakerid = ''

#     return activespeakerid
