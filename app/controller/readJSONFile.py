"""Module to read data from JSON file."""

import json

def readJSONFile(filepath):
    """_summary_

    Args:
        filepath : path to the JSON file

    Returns:
        JSONData
    """
    with open(filepath, 'r') as JSONFile:
        JSONData = json.load(JSONFile)

    return JSONData
    