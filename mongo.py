from pymongo import MongoClient

class MongoDBHelper:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="python", collection_name="stock"):
        """
        初始化 MongoDBHelper 实例，连接到 MongoDB 数据库和集合。

        :param uri: MongoDB 连接字符串，默认连接到 localhost:27017
        :param db_name: 数据库名称，默认为 'python'
        :param collection_name: 集合名称，默认为 'stock'
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_one(self, data):
        """
        向集合中插入单条数据。

        :param data: 要插入的数据字典
        """
        result = self.collection.insert_one(data)
        return result.inserted_id

    def insert_many(self, data_list):
        """
        向集合中插入多条数据。

        :param data_list: 要插入的数据字典列表
        """
        result = self.collection.insert_many(data_list)
        return result.inserted_ids

    def find_one(self, query):
        """
        根据查询条件查找单条数据。

        :param query: 查询条件字典
        :return: 查询到的单条数据，若没有匹配项则返回 None
        """
        result = self.collection.find_one(query)
        return result

    def find_many(self, query):
        """
        根据查询条件查找多条数据。

        :param query: 查询条件字典
        :return: 查询到的数据列表
        """
        results = self.collection.find(query)
        return list(results)

    def update_one(self, query, new_data):
        """
        更新单条数据。

        :param query: 查询条件字典
        :param new_data: 更新的数据字典
        :return: 更新的结果信息
        """
        result = self.collection.update_one(query, {"$set": new_data})
        return result.modified_count

    def update_many(self, query, new_data):
        """
        更新多条数据。

        :param query: 查询条件字典
        :param new_data: 更新的数据字典
        :return: 更新的结果信息
        """
        result = self.collection.update_many(query, {"$set": new_data})
        return result.modified_count

    def delete_one(self, query):
        """
        删除单条数据。

        :param query: 查询条件字典
        :return: 删除的结果信息
        """
        result = self.collection.delete_one(query)
        return result.deleted_count

    def delete_many(self, query):
        """
        删除多条数据。

        :param query: 查询条件字典
        :return: 删除的结果信息
        """
        result = self.collection.delete_many(query)
        return result.deleted_count

