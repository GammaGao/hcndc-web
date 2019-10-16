# -*- coding: utf-8 -*-

import pymongo


class MongoLinks(object):
    """mongo连接类"""

    def __init__(self, host, port, db, user=None, password=None):
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password
        self.conn = pymongo.MongoClient(host=self.host, port=self.port, serverSelectionTimeoutMS=10000)

        if self.user and self.password:
            db_auth = self.conn[self.db]
            db_auth.authenticate(self.user, self.password)

    def get_collection(self, collection):
        """获取集合"""
        collection = self.conn[self.db][collection]
        return collection

    def get_collection_all(self):
        """获取所有集合"""
        result = self.conn[self.db].list_collection_names()
        return result

    def is_exist(self, collection):
        """判断集合是否已存在"""
        result = self.conn[self.db].list_collection_names()
        return True if collection in result else False

    def insert_one(self, collection, document):
        """插入一条数据"""
        result = self.get_collection(collection).insert_one(document)
        return result.inserted_id

    def insert(self, collection, document):
        """插入数据"""
        result = self.get_collection(collection).insert(document)
        return result.inserted_id

    def remove(self, collection, document):
        """删除数据"""
        result = self.get_collection(collection).remove(document)
        return result

    def update(self, collection, document):
        """更新数据"""
        data = self.get_collection(collection).update({"_id": document["_id"]}, document)
        result = self.get_collection(collection).find_one({"_id": data["_id"]})
        return result

    def query_one(self, collection, document):
        """查找一条数据"""
        result = self.get_collection(collection).find_one(document)
        return result

    def query(self, collection, document):
        """查找数据"""
        result = list(self.get_collection(collection).find(document))
        return result

    def query_count(self, collection, document):
        """查询总数"""
        result = self.get_collection(collection).find(document).count()
        return result

    def query_search_page(self, collection, document, limit, offset):
        """分页"""
        result = list(self.get_collection(collection).find(document).limit(limit).skip(offset))
        return result


if __name__ == '__main__':
    opts = {
        "host": "172.16.163.8",
        "port": 27017,
        "db": "logs"
    }
    client = MongoLinks(**opts)
    _result = client.is_exist('site')
    print(_result)
