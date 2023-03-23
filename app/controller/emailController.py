import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def sendEmail(projectname, username, homelink, purpose, sender_email, receiver_email, 
sender_password, smtp_server="smtp.gmail.com", port=465, currentuserotp='', notification_text=''):

    context = ssl.create_default_context()
    # context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    email_draft = draftEmail(purpose, projectname, homelink, username, currentuserotp, notification_text)
    if email_draft != '':
        email_draft["From"] = sender_email
        email_draft["To"] = receiver_email
        # with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        try:
            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls(context=context)
                print ("Logging in")
                server.login(sender_email, sender_password)
                print ("Sending message")
                # server.sendmail(sender_email, receiver_email, email_text)
                server.send_message(email_draft,sender_email, receiver_email)
                print ("Message Sent!")
            return ('Project shared and email notification sent successfully!')    
        except Exception as e:
            return ('Project shared successfully but error in sending email' + str(e))



def draftEmail (purpose, projectname='', homelink='', username='',currentuserotp='', notification_text=''):
    draft = ''
    if purpose == 'share':
        draft = getShareEmail(projectname, homelink, username)
    elif purpose == 'OTP':
        draft = getOTPEmail(username, currentuserotp)
    elif purpose == 'notification':
        draft = getNotificationEmail(notification_text)

    return draft

def getShareEmail(projectname, homelink, username):
    message = MIMEMultipart("alternative")
    message["Subject"] = f"[LiFE App]: Project '{projectname}' shared with you"
    message_head = getEmailHead()
    message_txt = f"""\
            <html>
            {message_head}
             <body>
                <div class='emailbody'>
                <h2>Project <i>"{projectname}"</i> Shared</h2>                
                <h3>Project <font color="red">"{projectname}"</font> has been shared 
                with the user <font color="red">"{username}"</font> on the LiFE App</h3>
                <h4>Click on the following link to access the project</h4>
                <a class="button" href="{homelink}" target="_blank">Access {projectname}</a>

                <br>
                <b>NOTE: Change Active Project to <font color="red">"{projectname}"</font>
                in the LiFE App to access it.</b>
                </div>
            </body>
            </html>
        """
    part1 = MIMEText(message_txt, "html")
    message.attach(part1)
      
    return message       

def getOTPEmail(username, currentuserotp):
    message = MIMEMultipart("alternative")
    message["Subject"] = f"[LiFE App]: Password Reset OTP"
    message_head = getEmailHead()
    message_txt = f"""\
            <html>
            {message_head}
             <body>
                <div class='emailbody'>
                <h2>OTP to reset the password</h2>                
                <h3>Please enter the following OTP to reset the password for {username}</h3>
                <h4><b>{currentuserotp}</b></h4>
                </div>
            </body>
            </html>
        """  
    part1 = MIMEText(message_txt, "html")
    message.attach(part1)

    return message


def getNotificationEmail(notification_text):
    message = MIMEMultipart("alternative")
    message["Subject"] = f"[LiFE App]: Notification"
    message_head = getEmailHead()
    message_txt = f"""\
            <html>
            {message_head}
             <body>
                <div class='emailbody'>
                <h2>LiFE Notification</h2>                
                {notification_text}
                </div>
            </body>
            </html>
        """ 
    part1 = MIMEText(message_txt, "html")
    message.attach(part1) 
    return message


def getEmailHead():
    head = """\
            <head>
                <style>
                a.button {
                -webkit-appearance: button;
                -moz-appearance: button;
                appearance: button;

                text-decoration: none;

                background-color: green;
                color: white;
                padding: 14px 25px;
                text-align: center;
                display: inline-block;
                }

                button {
                background-color: #f44336;
                color: white;
                padding: 14px 25px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                border-style: groove;
                border-color: yellow;
                }
                
                h2{
                    background-color: blue;
                    color: white;
                    text-align: center;
                    border-style: groove;
                    border-color: yellow;
                    border: 2px solid yellow;
                    border-radius: 12px;
                    padding: 5px;
                }

                div.emailbody {
                    background-color: #F8F8FF;
                    border-style: ridge;
                    border-color: black;
                    border: 2px
                }

                </style>
            </head>
        """

    return head


def getSenderDetails(appconfigs):
    all_sender_details = {}

    sender_email_details = appconfigs.find_one(
                {
                    'configtype': 'emailsetup'
                },
                {
                    '_id': 0,
                    'configparams.notificationEmail': 1,
                    'configparams.notificationEmailPwd': 1,
                    'configparams.smtpPort': 1,
                    'configparams.smtpServer': 1,
                }
            )
    
    # print ('Sender details in database', sender_email_details)
    if 'configparams' in sender_email_details :
        all_sender_details['email'] = sender_email_details['configparams']['notificationEmail']
        all_sender_details['password'] = sender_email_details['configparams']['notificationEmailPwd']
        all_sender_details['port'] = sender_email_details['configparams']['smtpPort']
        all_sender_details['smtp_server'] = sender_email_details['configparams']['smtpServer']
    else:
        all_sender_details = {
        'email': '',
        'password': '',
        'port': '',
        'smtp_server': ''
        }

    return all_sender_details


def getCurrentUserEmail (userlogin, username):
    current_user_email = userlogin.find_one(
                {
                    'username': username
                },
                {
                    '_id': 0,
                    'userProfile.email': 1
                }
            )
    print ('Current user email', current_user_email)
    return current_user_email['userProfile']['email']


if __name__ == "__main__":
    ## For Gmail (disable 2-factor, etc)
    # port = 465  # For SSL
    # smtp_server = "smtp.gmail.com"

    ## For Outlook
    port = 587    
    smtp_server = "smtp.office365.com"
    # smtp_server = "smtp-mail.outlook.com"
    sender_email = "unreal.tece@outlook.com"  # Enter your address
    receiver_email = "riteshkr.kmi@gmail.com"  # Enter receiver address
    password = input("Type your password and press enter: ").strip()

    # message = """\
    # Subject: Hi there

    # This message is sent from Python."""

    message = MIMEMultipart("alternative")
    message["Subject"] = "[LiFE]: New Project shared with you"
    message["From"] = sender_email
    message["To"] = receiver_email

    message_txt = """\
            <html>
            <head>
                <style>
                a.button {
                -webkit-appearance: button;
                -moz-appearance: button;
                appearance: button;

                text-decoration: none;

                background-color: green;
                color: white;
                padding: 14px 25px;
                text-align: center;
                display: inline-block;
                }

                button {
                background-color: #f44336;
                color: white;
                padding: 14px 25px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                }
                
                h2{
                    background-color: blue;
                    color: white;
                    text-align: center;
                }

                div.emailbody {
                    background-color: yellow;
                }

                </style>
            </head>
            <body>
                <h2>New Project Shared</h2>
                <div class='emailbody'>
                <h3>A New Project has been shared with you on the LiFE App</h3>
                <h4>Click on the following link to access the project</h4>
                <a class="button" href="http://anno.ldcil.org:5001/" target="_blank">Open Project</a>
                </div>
            </body>
            </html>
    """
    part1 = MIMEText(message_txt, "html")
    message.attach(part1)

    sendEmail(message, sender_email, receiver_email, password, smtp_server, port)