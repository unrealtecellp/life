from app import mongo

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
