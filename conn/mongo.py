# -*- coding: utf-8 -*-

import pymongo


class MongoLinks(object):
    """mongo连接类"""

    def __init__(self, host, port, db, collection, user, password):
        self.host = host
        self.port = port
        self.db = db
        self.collection_name = collection
        self.user = user
        self.password = password
        self.conn = pymongo.MongoClient(host=self.host, port=self.port)

        if self.user and self.password:
            db_auth = self.conn[self.db]
            db_auth.authenticate(self.user, self.password)
            self.collection = self.conn[self.db][self.collection_name]
        else:
            self.collection = self.conn[self.db][self.collection_name]
