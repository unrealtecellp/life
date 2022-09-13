# # Generate OTP
# {'id': '9d78dff0-4f6e-483f-b90b-dbf157989e77',
#    'item': [{'id': '899156e4-6803-4c5d-8ef5-ef9c3c4e6f9c',
#      'name': 'Generate OTP',
#      'request': {'header': [{'key': 'access-code',
#         'type': 'text',
#         'value': '{{ACCESS_CODE}}'},
#        {'key': 'phone-number', 'type': 'text', 'value': '{{PHONE_NUMBER}}'}],
#       'method': 'PUT',
#       'url': '{{SERVER_URL}}/worker/otp/generate'},
#      'response': []},



########################## Register the ph. no. and get the audio file ################################################
# urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/worker/otp/generate'
# hederr= {'access-code':'59040473', 'phone-number':'9719009548'}
# r = requests.put(url = urll, headers = hederr) 
# r.json()


################################ Verfy the otp and get the id_token ###########################################################
# import requests
# urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/worker/otp/verify'
# hederr= {'access-code':'59040473', 'phone-number':'', 'otp':''}
# r = requests.put(url = urll, headers = hederr) 

# r.json()


################################## Get New Assignment ########################################################################################

import requests 

# karya_tokenid = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImExNWE0MGQ0In0.eyJzdWIiOiIyODE0NzQ5NzY3MTA3MDMiLCJlbnRpdHkiOiJ3b3JrZXIiLCJpYXQiOjE2NjI5MDI1NTIsImV4cCI6MTY2NTQ5NDU1MiwiYXVkIjoia2FyeWEtc2VydmVyIiwiaXNzIjoia2FyeWEtc2VydmVyIn0.Dvq44bd0RDdQeAGBP39bU-Hsedd_PJs2XpIbPNuTeR0'
urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=new&from=2021-05-11T07:23:40.654Z'
hederr= {'karya-id-token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImExNWE0MGQ0In0.eyJzdWIiOiIyODE0NzQ5NzY3MTA3MDMiLCJlbnRpdHkiOiJ3b3JrZXIiLCJpYXQiOjE2NjI5MDI1NTIsImV4cCI6MTY2NTQ5NDU1MiwiYXVkIjoia2FyeWEtc2VydmVyIiwiaXNzIjoia2FyeWEtc2VydmVyIn0.Dvq44bd0RDdQeAGBP39bU-Hsedd_PJs2XpIbPNuTeR0'}
requestid = requests.get(headers = hederr, url = urll) 
requestid.json()


######################################################### Get audio file ########################################################
# id = {':id': '281474976733174'}
urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignment/281474976733174/input_file'

hederr= {'karya-id-token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImExNWE0MGQ0In0.eyJzdWIiOiIyODE0NzQ5NzY3MTA3MDMiLCJlbnRpdHkiOiJ3b3JrZXIiLCJpYXQiOjE2NjI5MDI1NTIsImV4cCI6MTY2NTQ5NDU1MiwiYXVkIjoia2FyeWEtc2VydmVyIiwiaXNzIjoia2FyeWEtc2VydmVyIn0.Dvq44bd0RDdQeAGBP39bU-Hsedd_PJs2XpIbPNuTeR0'}

r_api= requests.get(url = urll, headers = hederr) 

request_data = r_api.content
print(request_data)

############################ convert binary audio file to .wav file and save system local storage ################
"""with open('myfile_1.wav', mode='bx') as f:
    f.write(request_data)"""
######################################## open the karya audio file in vlc ######################################



# import vlc
# from playsound import playsound
# audio_file = "/home/kmi/Desktop/myfile_1.wav"
# playsound(audio_file)

# audio_file = "/home/kmi/Desktop/myfile_1.wav"
# player = vlc.MediaPlayer(audio_file)
# player.play()

# import required module
import os

# play sound
file = "/home/kmi/Desktop/myfile_1.wav"
print('playing sound using native player')
os.system("afplay " + file)
