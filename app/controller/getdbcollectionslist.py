# getdbcollection.py
def getdbcollectionslist(mongo, *args):
    '''
    INPUT:
        mongo: instance of PyMongo
        *args: list of the collections name

    OUTPUT:
        dbcollections: tuple of collections instance
    '''

    # Select the 'lifedb' database
    db = mongo.cx['lifedb']

    if not args:
        # If no collection names are provided, get all collection names from 'lifedb'
        args = db.list_collection_names()
        
    dbcollectionslist = []
    for collection_name in args:
        dbcollectionslist.append(db[collection_name])

    return tuple(dbcollectionslist)
