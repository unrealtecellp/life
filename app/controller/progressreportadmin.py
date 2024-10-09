from pymongo import MongoClient
from collections import defaultdict
import math
from config import Config



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
