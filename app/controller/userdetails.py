import json


def getuserdetails(userlogin, username=""):

    if username == '':
        userdata = userlogin.find(
            {}, {'username': 1, 'userProfile': 1, 'isAdmin': 1, 'isActive': 1, 'userdeleteFLAG': 1, '_id': 0})
        userDetails = []
        for current_userdata in userdata:
            userDetails.append(current_userdata)
    else:
        print('Username', username)
        userDetails = userlogin.find_one(
            {'username': username}, {'username': 1, 'isAdmin': 1, 'userProfile': 1, '_id': 0})

    return userDetails


def updateuserstatus(
        userlogin, updateaction, userstatus, username):

    if updateaction == 'approve':
        if userstatus == 'ADMIN':
            userlogin.update_one(
                {'username': username}, {'$set': {'isActive': 1, 'isAdmin': 1}})
        else:
            userlogin.update_one(
                {'username': username}, {'$set': {'isActive': 1, 'isAdmin': 0}})
    elif updateaction == 'reject':
        userlogin.update_one(
            {'username': username}, {'$set': {'userdeleteFLAG': 1, 'isActive': 0}})
    elif updateaction == 'deactivate':
        userlogin.update_one(
            {'username': username}, {'$set': {'isActive': 2}})
    elif updateaction == 'delete':
        userlogin.update_one(
            {'username': username}, {'$set': {'userdeleteFLAG': 1, 'isActive': 2}})

    updatedUserDetails = getuserdetails(userlogin)

    return updatedUserDetails


def getuserprofilestructure(userlogin):
    userdata = userlogin.find(
        {'isActive': 1, 'userdeleteFLAG': 0}, {'userProfile': 1, '_id': 0})

    # print ('User Data', userdata)
    all_profile_info = []
    for current_userdata in userdata:
        # print(current_userdata, current_userdata['userProfile'])
        all_profile_info.extend(list(current_userdata['userProfile'].keys()))

    # print('Profile keys', list(all_profile_info))
    return list(set(all_profile_info))


def get_user_type(current_username, ADMIN_USER, SUB_ADMINS):
    if current_username == ADMIN_USER:
        usertype = 'SUPER-ADMIN'
    elif current_username in SUB_ADMINS:
        usertype = 'ADMIN'
    else:
        usertype = 'USER'

    return usertype


def get_admin_users(userlogin):
    super_admin = userlogin.find_one(
        {'isSuperAdmin': 1}, {'username': 1, '_id': 0})

    if super_admin is not None:
        super_admin = super_admin['username']

    all_admins = userlogin.find(
        {'isAdmin': 1}, {'username': 1, '_id': 0})

    admins = []
    for current_admin in all_admins:
        admins.append(current_admin['username'])

    return super_admin, admins
