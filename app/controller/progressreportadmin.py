from pymongo import MongoClient
from collections import defaultdict
import math
from config import Config
import datetime
import pandas as pd


# MongoDB URI from Config class
mongo_uri = Config.MONGO_URI




def convert_size(size_bytes):
    if size_bytes == 0:
        return "0", "B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s}", size_name[i]




def get_collection_stats(db_name, collection_name):
    # Connect to MongoDB (default connection)
    client = MongoClient()
    db = client[db_name]
    collection = db[collection_name]

    # Initialize dictionaries to collect unique keys and their values
    speaker_ids = defaultdict(set)
    speakers_audio_ids = defaultdict(list)

    # Iterate over all documents to collect the required data
    project_stats = []
    for doc in collection.find():
        # Initialize project data dictionary
        project_data = {
            "projectname": doc.get("projectname"),
            "projectOwner": doc.get("projectOwner"),
            "sharedwith": doc.get("sharedwith"),
            "projectDerivatives": doc.get("projectDerivatives"),
            "aboutproject": doc.get("aboutproject"),
            "projectType": doc.get("projectType"),
            "speakerIds": {},
            "speakersAudioIds": {},
            "totalAudioIds": 0,
            "speakersAudioIdsKeys": []
        }

        # Collect unique keys under speakerIds and their values
        if "speakerIds" in doc:
            for key, value in doc["speakerIds"].items():
                speaker_ids[key].update(value)
                project_data["speakerIds"][key] = value

        # Collect unique keys under speakersAudioIds and the count of their respective lists
        if "speakersAudioIds" in doc:
            total_audio_ids = 0
            for key, value in doc["speakersAudioIds"].items():
                speakers_audio_ids[key] = len(value)
                project_data["speakersAudioIds"][key] = value
                total_audio_ids += len(value)
                project_data["speakersAudioIdsKeys"].append(key)
            project_data["totalAudioIds"] = total_audio_ids

        # Add project data to the list
        project_stats.append(project_data)

    return project_stats, speaker_ids, speakers_audio_ids




# # Function to calculate the difference between two datetime strings
# def calculate_time_diff(start_time, end_time):
#     format_str = "%d/%m/%y %H:%M:%S"
#     start_dt = datetime.datetime.strptime(start_time, format_str)
#     end_dt = datetime.datetime.strptime(end_time, format_str)
    
#     total_seconds = (end_dt - start_dt).total_seconds()
#     hours = int(total_seconds // 3600)
#     minutes = int((total_seconds % 3600) // 60)
#     seconds = int(total_seconds % 60)
    
#     return total_seconds, f"{hours} hours, {minutes} minutes, {seconds} seconds"

# # Function to calculate total working time
# def calculate_working_time(access_times, update_times):
#     total_working_time = 0
#     for access_time, update_time in zip(access_times, update_times):
#         time_diff, _ = calculate_time_diff(access_time, update_time)
#         total_working_time += time_diff

#     hours = int(total_working_time // 3600)
#     minutes = int((total_working_time % 3600) // 60)
#     seconds = int(total_working_time % 60)
    
#     return total_working_time, f"{hours} hours, {minutes} minutes, {seconds} seconds"




# Function to calculate the difference between two datetime strings
def calculate_time_diff(start_time, end_time):
    # Create a Series from the start and end times
    start_series = pd.to_datetime(pd.Series(start_time), format="%d/%m/%y %H:%M:%S")
    end_series = pd.to_datetime(pd.Series(end_time), format="%d/%m/%y %H:%M:%S")

    # Calculate the time difference
    total_seconds = (end_series - start_series).dt.total_seconds()
    hours = (total_seconds // 3600).astype(int)
    minutes = ((total_seconds % 3600) // 60).astype(int)
    seconds = (total_seconds % 60).astype(int)

    return total_seconds.tolist(), [f"{h} hours, {m} minutes, {s} seconds" for h, m, s in zip(hours, minutes, seconds)]

# Function to calculate total working time
def calculate_working_time(access_times, update_times):
    # Convert access and update times to datetime Series
    access_series = pd.to_datetime(pd.Series(access_times), format="%d/%m/%y %H:%M:%S")
    update_series = pd.to_datetime(pd.Series(update_times), format="%d/%m/%y %H:%M:%S")

    # Calculate the total working time
    total_working_time = (update_series - access_series).dt.total_seconds().sum()

    hours = int(total_working_time // 3600)
    minutes = int((total_working_time % 3600) // 60)
    seconds = int(total_working_time % 60)

    return total_working_time, f"{hours} hours, {minutes} minutes, {seconds} seconds"

