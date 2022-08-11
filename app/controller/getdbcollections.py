'''Module provide a function to get the collection instance.'''
def getdbcollections(mongo, *args):
    '''
    INPUT:
        mongo: instance of PyMongo
        *args: list of the collections name

    OUTPUT:
        dbcollections: tuple of collections instance
    '''

    dbcollections = []
    for collection_name in args:
        dbcollections.append(mongo.db[collection_name])

    return tuple(dbcollections)
