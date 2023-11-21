from app import mongo
from app.controller import (
    life_logging
)

logger = life_logging.get_logger()

def generateDummyAppConfig():
    try:
        mongo.db.validate_collection("lifeappconfigs")
    except Exception as e:
        print ('Mongo error', e)
        lifeappconfigs = mongo.db.lifeappconfigs
        allconfigdocs = lifeappconfigs.find_one(
            {
                'configtype': 'emailsetup'
            },
            {
                '_id': 0,
                'notificationEmail': 1
            }
        )
        if allconfigdocs == None:
            generateDummyEmailConfig(lifeappconfigs)
        elif 'notificationEmail' not in allconfigdocs:
            generateDummyEmailConfig(lifeappconfigs)

def generateDummyEmailConfig(lifeappconfigs):
    lifeappconfigs.insert_one({
        'configtype': 'emailsetup',
        'configparams': {
            'notificationEmail': '',
            'notificationEmailPwd': '',
            'smtpPort': '',
            'smtpServer': '',
        }
    })

def getAppSendEmailDetails(lifeappconfigs):
    send_email_details = {}
    label_map = {
        'notificationEmail': 'Email for Notification',
        'notificationEmailPwd': 'Password of the Email',
        'smtpServer': 'SMTP Server to be used',
        'smtpPort': 'SMTP Port to be used'
    }
    allconfigdocs = lifeappconfigs.find_one(
            {
                'configtype': 'emailsetup'
            },
            {
                '_id': 0,
                'configparams': 1
            }
        )
    all_config_params = allconfigdocs['configparams']
    # send_email_details['Email for Notification'] = all_config_params['notificationEmail']
    # send_email_details['Password of the Email'] = all_config_params['notificationEmailPwd']
    # send_email_details['SMTP Server to be used'] = all_config_params['smtpServer']
    # send_email_details['SMTP Port to be used'] = all_config_params['smtpPort']

    print ("All config docs", all_config_params)
    return all_config_params, label_map

def getHuggingFaceModelConfig(lifeappconfigs, current_username, usertype='SUPER-ADMIN'):
    label_map = {
        'authorsList': 'List of Featured Authors',
        'taskType': 'HuggingFace Task'
    }
    allconfigdocs = lifeappconfigs.find_one(
            {
                'configtype': 'huggingfacemodel'
            },
            {
                '_id': 0,
                'configparams': 1
            }
        )
    default_entry = {
        'globals': 
            {'automatic-speech-recognition': 
                {'authorsList': []}
            }
        ,
        'usersData': 
            {current_username: 
                {'apiTokens': [],
                'globals': 
                    {'automatic-speech-recognition': 
                        {'authorsList': []}
                    }
                }
            }        
    }
    
    if allconfigdocs is not None:
        all_config_params = allconfigdocs.get('configparams', default_entry)
    else:
        all_config_params = default_entry
        lifeappconfigs.insert_one(
            {
                'configtype': 'huggingfacemodel',
                'configparams': default_entry
            }
        )

    logger.debug ("All config docs %s", all_config_params)
    return all_config_params, label_map

def updateAppSendEmailDetails(lifeappconfigs, updatedata):
    update_details={'configparams': updatedata}
    label_map = {
        'notificationEmail': 'Email for Notification',
        'notificationEmailPwd': 'Password of the Email',
        'smtpServer': 'SMTP Server to be used',
        'smtpPort': 'SMTP Port to be used'
    }
    lifeappconfigs.update_one(
            {
                'configtype': 'emailsetup'
            },
            {
                '$set': update_details
            }
        )

    return label_map

def updateHuggingFaceModelConfig(lifeappconfigs, updatedata):
    update_details={'configparams': updatedata}
    label_map = {
        'authorsList': 'List of Featured Authors',
        'taskType': 'HuggingFace Task'
    }
    logger.debug('Update Data %s', update_details)
    lifeappconfigs.update_one(
            {
                'configtype': 'huggingfacemodel'
            },
            {
                '$set': update_details
            }
        )

    return label_map