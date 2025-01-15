from pymongo import MongoClient

class MongoDeviceManager:
    def __init__(self, host, port, database, collection, username, password):
        self.client = MongoClient(
            host=host,
            port=port,
            username=username,
            password=password,
        )
        self.db = self.client[database]
        self.collection = self.db[collection]

    def get_devices(self):
        devices = self.collection.find({}, {"_id": 0, "ip_admin": 1, "hostname": 1})
        return [doc for doc in devices]

    def close(self):
        self.client.close()
