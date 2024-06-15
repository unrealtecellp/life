def getdbcollections(mongo, *args):
    '''
    INPUT:
        mongo: instance of PyMongo
        *args: list of the collections name

    OUTPUT:
        dbcollections: tuple of collections instance
    '''

    if not args:
        # If no collection names are provided, get all collection names
        args = mongo.db.list_collection_names()
        
    dbcollections = []
    for collection_name in args:
        dbcollections.append(mongo.db[collection_name])

    return tuple(dbcollections)